"""Role-specific provider interfaces (ADR-0002) and their deterministic fakes.

Three model roles, each swappable independently without touching the pipeline:
Wording/Concepts (LLM), Background generation (image model), Critique (VLM).
Binding is configuration (THUMB_PROVIDERS env var), never a code change.
Fakes need no network and no API key.
"""

import hashlib
import os
from dataclasses import dataclass
from typing import Protocol

from PIL import Image


class WordingProvider(Protocol):
    def propose_wordings(self, title: str, hook: str, n: int) -> list[str]: ...


class BackgroundProvider(Protocol):
    def generate_background(self, prompt: str, size: tuple[int, int]) -> Image.Image: ...


class CritiqueProvider(Protocol):
    def review(self, image: Image.Image, checklist: list[str]) -> dict: ...


class FakeWordingProvider:
    SUFFIXES = ["", "EXPOSED", "SECRETS", "NOW", "THE TRUTH"]

    def propose_wordings(self, title, hook, n):
        base = " ".join(title.upper().split()[:3]) or "UNTITLED"
        return [f"{base} {suffix}".strip() for suffix in self.SUFFIXES[:n]]


class FakeBackgroundProvider:
    def generate_background(self, prompt, size):
        digest = hashlib.sha256(prompt.encode("utf-8")).digest()
        base = tuple(v // 2 for v in digest[:3])  # dark half-range
        accent = tuple(128 + v // 2 for v in digest[3:6])  # light half-range
        image = Image.new("RGB", size, base)
        band = Image.new("RGB", (size[0], size[1] // 5), accent)
        image.paste(band, (0, size[1] // 3))
        return image


class FakeCritiqueProvider:
    def review(self, image, checklist):
        return {"defects": []}


@dataclass
class Providers:
    wording: WordingProvider
    background: BackgroundProvider
    critique: CritiqueProvider


def get_providers(name=None):
    name = name or os.environ.get("THUMB_PROVIDERS", "fake")
    if name == "fake":
        return Providers(
            wording=FakeWordingProvider(),
            background=FakeBackgroundProvider(),
            critique=FakeCritiqueProvider(),
        )
    raise SystemExit(f"unknown provider binding: {name!r} (available: fake)")
