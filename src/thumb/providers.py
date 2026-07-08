"""Role-specific provider interfaces (ADR-0002) and their deterministic fakes.

Three model roles, each swappable independently without touching the pipeline:
Wording/Concepts (LLM), Background generation (image model), Critique (VLM).
Binding is configuration (THUMB_PROVIDERS env var), never a code change.
Fakes need no network and no API key.
"""

import functools
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image

RETRY_ATTEMPTS = 5


class TransientProviderError(Exception):
    """A 503/429-class failure worth retrying (the prototype hit these
    frequently on flash-lite under load)."""


def _is_transient(exc):
    if isinstance(exc, TransientProviderError):
        return True
    # google-genai errors (ServerError/ClientError) carry the HTTP code
    return getattr(exc, "code", None) in (429, 503)


def retry_transient(fn):
    """Retry with exponential backoff on transient failures. Lives in the
    provider layer so a half-finished Order never dies to one 503."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        base = float(os.environ.get("THUMB_RETRY_BASE_SECONDS", "2"))
        for attempt in range(RETRY_ATTEMPTS):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                if not _is_transient(exc) or attempt == RETRY_ATTEMPTS - 1:
                    raise
                time.sleep(min(base * 2**attempt, 30))

    return wrapper


class CallLog:
    """Journal of provider calls, written by fakes so tests (and the operator)
    can observe from disk exactly which model calls a command made."""

    def __init__(self, path):
        self.path = Path(path)

    def record(self, provider, method, detail):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"provider": provider, "method": method, "detail": str(detail)},
                    sort_keys=True,
                )
                + "\n"
            )


class _NullLog:
    def record(self, provider, method, detail):
        pass


class Ledger:
    """Raw per-call cost writes (PRD story 35, raw writes only). One JSON line
    per model call: role, model, units consumed, cost. Reporting comes in a
    later milestone; the data just has to land. Never contains the API key."""

    def __init__(self, path):
        self.path = Path(path)

    def add(self, role, method, model, units, cost_usd):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "role": role,
                        "method": method,
                        "model": model,
                        "units": units,
                        "cost_usd": round(cost_usd, 6),
                    },
                    sort_keys=True,
                )
                + "\n"
            )


class _NullLedger:
    def add(self, role, method, model, units, cost_usd):
        pass


class WordingProvider(Protocol):
    """The LLM seat (ADR-0002): Wording copywriting AND Concept ideation."""

    def propose_wordings(self, title: str, hook: str, n: int) -> list[str]: ...

    def propose_concepts(self, title: str, hook: str, backdrop: str, n: int) -> list[str]: ...


class BackgroundProvider(Protocol):
    def generate_background(self, prompt: str, size: tuple[int, int]) -> Image.Image: ...


class CritiqueProvider(Protocol):
    """The VLM seat (ADR-0002): Candidate review AND one-time photo analysis."""

    def review(self, image: Image.Image, checklist: list[str]) -> dict: ...

    def analyze_photo(self, photo_path) -> dict: ...

    def extract_style_spec(self, reference_path) -> dict: ...


class FakeWordingProvider:
    """Deterministic copywriting stand-in: 3-5 word ALL-CAPS lines built around
    the title's lead word — never an echo of the title itself."""

    def __init__(self, log=None, ledger=None):
        self._log = log or _NullLog()
        self._ledger = ledger or _NullLedger()

    def propose_wordings(self, title, hook, n):
        self._log.record("wording", "propose_wordings", title)
        self._ledger.add("wording", "propose_wordings", "fake", {"calls": 1}, 0.0)
        lead = (title.upper().split() or ["THIS"])[0]
        proposals = [
            f"WHY {lead}S FAIL YOU",
            f"THE {lead} MISTAKE",
            f"STOP BREAKING YOUR {lead}S",
            f"THE TRUTH ABOUT {lead}S",
            f"{lead}S DONE RIGHT",
        ]
        return proposals[:n]

    def propose_concepts(self, title, hook, backdrop, n):
        self._log.record("wording", "propose_concepts", f"{title} | {backdrop}")
        self._ledger.add("wording", "propose_concepts", "fake", {"calls": 1}, 0.0)
        lead = (title.lower().split() or ["the idea"])[0]
        glyphs = [
            "circular-arrows glyph",
            "glossy infinity symbol",
            "cracked gear",
            "tangled wire knot",
        ]
        return [
            f"ONE bold minimalist {glyph} suggesting {lead}, floating off-center"
            for glyph in glyphs[:n]
        ]


class FakeBackgroundProvider:
    def __init__(self, log=None, ledger=None):
        self._log = log or _NullLog()
        self._ledger = ledger or _NullLedger()
        # THUMB_FAKE_503S=N scripts the first N calls to fail transiently, so
        # tests can prove retry/backoff at the seam with no real network
        self._fail_remaining = int(os.environ.get("THUMB_FAKE_503S", "0"))

    @retry_transient
    def generate_background(self, prompt, size):
        if self._fail_remaining > 0:
            self._fail_remaining -= 1
            self._log.record("background", "transient-503", prompt)
            raise TransientProviderError("scripted 503")
        self._log.record("background", "generate_background", prompt)
        self._ledger.add("background", "generate_background", "fake", {"images": 1}, 0.0)
        digest = hashlib.sha256(prompt.encode("utf-8")).digest()
        base = tuple(v // 2 for v in digest[:3])  # dark half-range
        accent = tuple(128 + v // 2 for v in digest[3:6])  # light half-range
        image = Image.new("RGB", size, base)
        band = Image.new("RGB", (size[0], size[1] // 5), accent)
        image.paste(band, (0, size[1] // 3))
        return image


class FakeCritiqueProvider:
    """Deterministic VLM stand-in. `analyze_photo` reads attributes from
    filename tokens so tests control analysis through inputs alone:
    point-left/point-right, gaze-left/gaze-right, shock/grimace/joy/curious,
    flat (light), busy (background), filtered, shirt-text.

    `extract_style_spec` tokens: grunge-wall/paper/black (backdrop),
    chips/label-bars (text device; default plain-accent),
    red/yellow/teal (accent color).
    """

    BACKDROPS = {
        "grunge-wall": "red-orange grunge wall texture, one flat color field",
        "paper": "warm paper texture with soft grain",
        "black": "near-black textured backdrop with subtle grain",
    }
    ACCENTS = {"red": "#D82C2C", "yellow": "#F2C200", "teal": "#12B5A5"}

    EXPRESSIONS = ("shock", "grimace", "joy", "curious")

    def __init__(self, log=None, ledger=None):
        self._log = log or _NullLog()
        self._ledger = ledger or _NullLedger()

    def review(self, image, checklist):
        self._log.record("critique", "review", "candidate")
        self._ledger.add("critique", "review", "fake", {"calls": 1}, 0.0)
        return {"defects": []}

    def analyze_photo(self, photo_path):
        self._log.record("critique", "analyze_photo", Path(photo_path).name)
        self._ledger.add("critique", "analyze_photo", "fake", {"calls": 1}, 0.0)

        stem = Path(photo_path).stem.lower()
        gesture = next(
            (g for g in ("point-left", "point-right") if g in stem), "none"
        )
        gaze = next((f"gaze-{d}"[5:] for d in ("left", "right") if f"gaze-{d}" in stem), "camera")
        expression = next((e for e in self.EXPRESSIONS if e in stem), "neutral")
        return {
            "gesture": gesture,
            "gaze": gaze,
            "expression": expression,
            "clothing_text": "shirt-text" in stem,
            "crops": ["full", "head-shoulders"],
            "lighting": "flat" if "flat" in stem else "directional",
            "background": "busy" if "busy" in stem else "plain",
            "filtered": "filtered" in stem,
        }

    def extract_style_spec(self, reference_path):
        stem = Path(reference_path).stem.lower()
        self._log.record("critique", "extract_style_spec", Path(reference_path).name)
        self._ledger.add("critique", "extract_style_spec", "fake", {"calls": 1}, 0.0)

        backdrop = next(
            (text for token, text in self.BACKDROPS.items() if token in stem),
            "textured color-field backdrop, one flat color",
        )
        device = next(
            (d for d in ("chips", "label-bars") if d in stem), "plain-accent"
        )
        accent = next(
            (hex_ for token, hex_ in self.ACCENTS.items() if token in stem), "#D82C2C"
        )
        return {
            "backdrop": backdrop,
            "palette": ["#202020", "#F5EFE6", accent],
            "accent": accent,
            "text_device": device,
            "icon_usage": "one simple bold icon supporting the concept",
            "subject_treatment": "studio-lit cutout, palette-tinted toward the backdrop",
            "composition": "2-line text left with one accent word, subject right, generous negative space",
        }


class CutoutEngine(Protocol):
    """Background removal. Not an API model role (ADR-0002's three seats), but
    bound with the providers so fake mode stays offline and dependency-light;
    the real binding is rembg."""

    def cut(self, photo_path) -> Image.Image: ...


class FakeCutoutEngine:
    """Oval matte: opaque center, transparent surround. Enough to exercise
    every downstream consumer of an RGBA cutout."""

    def cut(self, photo_path):
        from PIL import ImageDraw

        with Image.open(photo_path) as photo:
            cutout = photo.convert("RGBA")
        mask = Image.new("L", cutout.size, 0)
        width, height = cutout.size
        ImageDraw.Draw(mask).ellipse(
            [width // 8, height // 12, width * 7 // 8, height], fill=255
        )
        cutout.putalpha(mask)
        return cutout


@dataclass
class Providers:
    wording: WordingProvider
    background: BackgroundProvider
    critique: CritiqueProvider
    cutout: CutoutEngine


def get_providers(root=".", name=None, ledger_path=None):
    name = name or os.environ.get("THUMB_PROVIDERS", "fake")
    # non-Order calls (onboarding analysis, style extraction) bill to the
    # workspace ledger; `order run` redirects to the Order's own ledger
    ledger = Ledger(ledger_path or Path(root) / ".thumb" / "ledger.jsonl")
    if name == "fake":
        log = CallLog(Path(root) / ".thumb" / "provider-calls.jsonl")
        return Providers(
            wording=FakeWordingProvider(log, ledger),
            background=FakeBackgroundProvider(log, ledger),
            critique=FakeCritiqueProvider(log, ledger),
            cutout=FakeCutoutEngine(),
        )
    if name == "gemini":
        from thumb import gemini  # deferred: fake mode must not need the SDK

        return gemini.bind(root, ledger)
    raise SystemExit(f"unknown provider binding: {name!r} (available: fake, gemini)")
