"""Real Gemini bindings for the three provider seats (ADR-0002), plus rembg
cutouts. Selected by THUMB_PROVIDERS=gemini — never a pipeline code change.

Model IDs and pricing verified against https://ai.google.dev/gemini-api/docs/pricing
on 2026-07-08 (they shift — re-check before trusting the cost constants):
  gemini-2.5-flash-lite         $0.10/M in (text+image), $0.40/M out
  gemini-3.1-flash-lite-image   $0.25/M in, $30/M image-out = $0.0336 per 1K image
Do NOT use the -preview aliases; gemini-3.1-flash-lite-preview is discontinued
2026-07-09.

Key hygiene: GEMINI_API_KEY comes from the environment or the workspace .env
(gitignored). It is passed to the SDK client and nowhere else — never printed,
never journaled, never written to metadata or the ledger.
"""

import io
import json
import os
from pathlib import Path

from PIL import Image

from thumb.providers import Providers, TransientProviderError, retry_transient

TEXT_MODEL = "gemini-2.5-flash-lite"  # LLM seat and VLM seat (PRD)
IMAGE_MODEL = "gemini-3.1-flash-lite-image"

TEXT_IN_PER_M, TEXT_OUT_PER_M = 0.10, 0.40
IMAGE_IN_PER_M = 0.25
PRICE_PER_IMAGE = 0.0336  # 1K image = 1120 output tokens @ $30/M


def _load_key(root):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        dotenv = Path(root) / ".env"
        if dotenv.is_file():
            for line in dotenv.read_text(encoding="utf-8").splitlines():
                name, _, value = line.partition("=")
                if name.strip() == "GEMINI_API_KEY":
                    key = value.strip().strip("'\"")
                    break
    if not key:
        raise SystemExit(
            "GEMINI_API_KEY not set — export it, or put GEMINI_API_KEY=... in "
            ".env at the workspace root (gitignored). Paid tier, ADR-0002."
        )
    return key


def _client(key):
    try:
        from google import genai
    except ImportError:
        raise SystemExit(
            "the gemini binding needs the google-genai package: "
            "pip install google-genai (and rembg for cutouts)"
        ) from None
    return genai.Client(api_key=key)


def _text_cost(response):
    usage = response.usage_metadata
    tokens_in = usage.prompt_token_count or 0
    tokens_out = (usage.candidates_token_count or 0) + (
        getattr(usage, "thoughts_token_count", 0) or 0
    )
    cost = tokens_in / 1e6 * TEXT_IN_PER_M + tokens_out / 1e6 * TEXT_OUT_PER_M
    return {"tokens_in": tokens_in, "tokens_out": tokens_out}, cost


def _parse_model_json(text):
    """The real model sometimes breaks JSON mode's promise of a bare payload:
    markdown fences around the object, prose before or after it (seen live
    2026-07-12, crashed onboarding). Try the clean parse, then fall back to
    the first parseable JSON value anywhere in the text."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for i, char in enumerate(text):
        if char in "{[":
            try:
                value, _ = decoder.raw_decode(text, i)
                return value
            except json.JSONDecodeError:
                continue
    # a reply with no JSON at all is a one-off model wobble: worth a retry,
    # never worth killing a half-finished Order
    raise TransientProviderError(f"model returned no parseable JSON: {text[:120]!r}")


def _json_call(client, contents):
    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=contents,
        config={"response_mime_type": "application/json"},
    )
    return _parse_model_json(response.text), response


def _image_part(path_or_image):
    from google.genai import types

    if isinstance(path_or_image, Image.Image):
        buf = io.BytesIO()
        path_or_image.save(buf, format="PNG")
        return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
    path = Path(path_or_image)
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime)


class GeminiWordingProvider:
    """The LLM seat: Wording copywriting and Concept ideation."""

    def __init__(self, client, ledger):
        self._client = client
        self._ledger = ledger

    @retry_transient
    def propose_wordings(self, title, hook, n):
        prompt = (
            f"You are a YouTube thumbnail copywriter for tech/education creators.\n"
            f'Video title: "{title}". Hook: "{hook}".\n\n'
            f"Return a JSON array of exactly {n} thumbnail text options. Each is "
            f"3-5 words, ALL CAPS, punchy and curiosity-driven — what makes a "
            f"viewer stop scrolling. NEVER just repeat the title. JSON array of "
            f"strings only."
        )
        proposals, response = _json_call(self._client, prompt)
        units, cost = _text_cost(response)
        self._ledger.add("wording", "propose_wordings", TEXT_MODEL, units, cost)
        proposals = [str(p).strip() for p in proposals if str(p).strip()]
        if not proposals:
            raise RuntimeError("wording provider returned no usable proposals")
        return proposals[:n]

    @retry_transient
    def propose_concepts(self, title, hook, backdrop, n):
        prompt = (
            f"You are a YouTube thumbnail art director.\n"
            f'Video title: "{title}". Hook: "{hook}".\n'
            f'The background style is: "{backdrop}".\n\n'
            f"Return a JSON array of exactly {n} visual concepts for the "
            f"background of this thumbnail. Each is ONE sentence describing ONE "
            f"bold simple graphic element (an icon-like object or symbol) that "
            f"embodies the video's idea — concrete and drawable, suited to flat "
            f"graphic design. NO people, NO faces, NO text or letters. "
            f"JSON array of strings only."
        )
        concepts, response = _json_call(self._client, prompt)
        units, cost = _text_cost(response)
        self._ledger.add("wording", "propose_concepts", TEXT_MODEL, units, cost)
        concepts = [str(c).strip() for c in concepts if str(c).strip()]
        if not concepts:
            raise RuntimeError("concept provider returned no usable concepts")
        return concepts[:n]


class GeminiBackgroundProvider:
    def __init__(self, client, ledger):
        self._client = client
        self._ledger = ledger

    @retry_transient
    def generate_background(self, prompt, size):
        from google.genai import types

        response = self._client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="16:9"),
            ),
        )
        image = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(io.BytesIO(part.inline_data.data))
                break
        tokens_in = response.usage_metadata.prompt_token_count or 0
        if image is None:
            # text-only reply (e.g. safety refusal): the tokens were still
            # spent, so bill them, then let the retry take one more swing
            self._ledger.add(
                "background", "generate_background", IMAGE_MODEL,
                {"images": 0, "tokens_in": tokens_in}, tokens_in / 1e6 * IMAGE_IN_PER_M,
            )
            raise TransientProviderError("no image in response")
        cost = PRICE_PER_IMAGE + tokens_in / 1e6 * IMAGE_IN_PER_M
        self._ledger.add(
            "background", "generate_background", IMAGE_MODEL,
            {"images": 1, "tokens_in": tokens_in}, cost,
        )
        return image


class GeminiCritiqueProvider:
    """The VLM seat: Candidate review, one-time photo analysis, and
    reference -> style-spec extraction. Each call asks for exactly the JSON
    shape the fakes model (the pipeline's real contract)."""

    def __init__(self, client, ledger):
        self._client = client
        self._ledger = ledger

    @retry_transient
    def review(self, image, checklist):
        rules = "\n".join(f"- {item}" for item in checklist)
        contents = [
            _image_part(image),
            "This is a YouTube thumbnail candidate. Check it against this "
            f"defect checklist:\n{rules}\n\n"
            'Return JSON: {"defects": [<short string per defect found, '
            "empty list if clean>]}. JSON only.",
        ]
        verdict, response = _json_call(self._client, contents)
        units, cost = _text_cost(response)
        self._ledger.add("critique", "review", TEXT_MODEL, units, cost)
        return {"defects": [str(d) for d in verdict.get("defects", [])]}

    @retry_transient
    def analyze_photo(self, photo_path):
        contents = [
            _image_part(photo_path),
            "Analyze this creator photo for YouTube thumbnail use. Return JSON "
            "with exactly these keys:\n"
            '{"gesture": "none"|"point-left"|"point-right",\n'
            ' "gaze": "camera"|"left"|"right",\n'
            ' "expression": "neutral"|"shock"|"grimace"|"joy"|"curious",\n'
            ' "clothing_text": true if clothing has readable text/logos,\n'
            ' "crops": ["full", "head-shoulders"] — the crops that would work,\n'
            ' "lighting": "flat"|"directional",\n'
            ' "background": "plain"|"busy",\n'
            ' "filtered": true if a beauty/color filter is visible}\n'
            "JSON only.",
        ]
        analysis, response = _json_call(self._client, contents)
        units, cost = _text_cost(response)
        self._ledger.add("critique", "analyze_photo", TEXT_MODEL, units, cost)
        return analysis

    @retry_transient
    def extract_style_spec(self, reference_path):
        contents = [
            _image_part(reference_path),
            "This is an admired YouTube thumbnail used as a style reference. "
            "Extract its style as JSON with exactly these keys:\n"
            '{"backdrop": one sentence describing the background treatment '
            "(texture, color field, gradient),\n"
            ' "palette": [3 hex colors: dominant, secondary, accent],\n'
            ' "accent": the single accent hex color,\n'
            ' "text_device": "chips"|"label-bars"|"plain-accent" — chips = text '
            "on torn-paper/rounded light chips, label-bars = text on solid "
            "rectangular bars, plain-accent = bare bold text with one accent "
            "word,\n"
            ' "icon_usage": one sentence on how icons/graphic elements are used,\n'
            ' "subject_treatment": one sentence on how the person is lit/graded,\n'
            ' "composition": one sentence on the layout}\n'
            "JSON only.",
        ]
        spec, response = _json_call(self._client, contents)
        units, cost = _text_cost(response)
        self._ledger.add("critique", "extract_style_spec", TEXT_MODEL, units, cost)
        return spec


class RembgCutoutEngine:
    """Real background removal (local, free — not an API seat)."""

    def cut(self, photo_path):
        try:
            from rembg import remove
        except ImportError:
            raise SystemExit(
                "the gemini binding needs rembg for cutouts: pip install rembg"
            ) from None
        with Image.open(photo_path) as photo:
            cutout = remove(photo.convert("RGB"))
        box = cutout.getbbox()
        return cutout.crop(box) if box else cutout


def bind(root, ledger):
    client = _client(_load_key(root))
    return Providers(
        wording=GeminiWordingProvider(client, ledger),
        background=GeminiBackgroundProvider(client, ledger),
        critique=GeminiCritiqueProvider(client, ledger),
        cutout=RembgCutoutEngine(),
    )
