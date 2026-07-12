"""Offline stand-in for the google-genai SDK, shadowed in via PYTHONPATH.

Lets seam tests drive the REAL gemini.py binding (THUMB_PROVIDERS=gemini)
with no network and no credits. Replays the response shape the real VLM
produced in the 2026-07-12 onboarding crash: the JSON payload wrapped in
markdown code fences with trailing prose — not the clean JSON that
response_mime_type promises.
"""

import json

from . import types  # noqa: F401  (google.genai.types must be importable)


class _Usage:
    prompt_token_count = 120
    candidates_token_count = 60
    thoughts_token_count = 0


class _Response:
    def __init__(self, text):
        self.text = text
        self.usage_metadata = _Usage()
        self.candidates = []


# What the real model actually sent back (shape-wise) despite JSON mode:
# fences around the object, commentary after the closing fence.
_ANALYSIS = {
    "gesture": "none",
    "gaze": "camera",
    "expression": "shock",
    "clothing_text": False,
    "crops": ["full", "head-shoulders"],
    "lighting": "directional",
    "background": "plain",
    "filtered": False,
}
_FENCED = (
    "```json\n"
    + json.dumps(_ANALYSIS, indent=2)
    + "\n```\n\nThis photo has directional lighting and a plain background."
)


class _Models:
    def generate_content(self, model=None, contents=None, config=None):
        return _Response(_FENCED)


class Client:
    def __init__(self, api_key=None):
        self.models = _Models()
