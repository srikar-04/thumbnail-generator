"""Role-specific provider interfaces (ADR-0002) and their deterministic fakes.

Three model roles, each swappable independently without touching the pipeline:
Wording/Concepts (LLM), Background generation (image model), Critique (VLM).
Binding is configuration (THUMB_PROVIDERS env var), never a code change.
Fakes need no network and no API key.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image


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


class WordingProvider(Protocol):
    def propose_wordings(self, title: str, hook: str, n: int) -> list[str]: ...


class BackgroundProvider(Protocol):
    def generate_background(self, prompt: str, size: tuple[int, int]) -> Image.Image: ...


class CritiqueProvider(Protocol):
    """The VLM seat (ADR-0002): Candidate review AND one-time photo analysis."""

    def review(self, image: Image.Image, checklist: list[str]) -> dict: ...

    def analyze_photo(self, photo_path) -> dict: ...


class FakeWordingProvider:
    SUFFIXES = ["", "EXPOSED", "SECRETS", "NOW", "THE TRUTH"]

    def __init__(self, log=None):
        self._log = log or _NullLog()

    def propose_wordings(self, title, hook, n):
        self._log.record("wording", "propose_wordings", title)
        base = " ".join(title.upper().split()[:3]) or "UNTITLED"
        return [f"{base} {suffix}".strip() for suffix in self.SUFFIXES[:n]]


class FakeBackgroundProvider:
    def __init__(self, log=None):
        self._log = log or _NullLog()

    def generate_background(self, prompt, size):
        self._log.record("background", "generate_background", prompt)
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
    """

    EXPRESSIONS = ("shock", "grimace", "joy", "curious")

    def __init__(self, log=None):
        self._log = log or _NullLog()

    def review(self, image, checklist):
        self._log.record("critique", "review", "candidate")
        return {"defects": []}

    def analyze_photo(self, photo_path):
        self._log.record("critique", "analyze_photo", Path(photo_path).name)

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


def get_providers(root=".", name=None):
    name = name or os.environ.get("THUMB_PROVIDERS", "fake")
    if name == "fake":
        log = CallLog(Path(root) / ".thumb" / "provider-calls.jsonl")
        return Providers(
            wording=FakeWordingProvider(log),
            background=FakeBackgroundProvider(log),
            critique=FakeCritiqueProvider(log),
            cutout=FakeCutoutEngine(),
        )
    raise SystemExit(f"unknown provider binding: {name!r} (available: fake)")
