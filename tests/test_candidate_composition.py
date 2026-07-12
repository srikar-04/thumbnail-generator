"""Ticket 09 — candidate composition at the CLI-over-disk seam.

Style-conditioned generation + the prototype's validated compositor recipe.
All assertions are on disk artifacts only (candidate images, metadata JSON,
persisted prompts, the fakes' call journal) — never on internals.
"""

import json
from pathlib import Path

from PIL import Image

from test_order_run import start_order

SEED_DIR = Path(__file__).parent.parent / "src" / "thumb" / "styles"

# the prototype's restraint rules — the single biggest quality lever (PRD)
RESTRAINT_RULES = (
    "one focal element",
    "generous negative space",
    "one accent color",
    "no clutter",
)


def seed_spec(name):
    return json.loads(
        (SEED_DIR / "tech-explainer" / f"{name}.json").read_text(encoding="utf-8")
    )


def read_meta(png):
    return json.loads(png.with_suffix(".json").read_text(encoding="utf-8"))


def candidates(order_dir):
    return sorted((order_dir / "candidates").glob("*.png"))


def test_default_run_spreads_candidates_across_style_specs(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)

    thumb("order", "run", "srikar", "001")

    pngs = candidates(order_dir)
    assert len(pngs) == 20  # ~20 Candidates is the real default, not the skeleton's 3

    specs_used = set()
    for png in pngs:
        meta = read_meta(png)
        assert meta["style_spec"], f"{png.name} must record which style spec it used"
        assert meta["wording"], f"{png.name} must record its wording"
        assert meta["source_photo"] == "face01.png"
        specs_used.add(meta["style_spec"])

    # the Contact Sheet must show genuinely different directions
    assert len(specs_used) >= 2, f"candidates only used {specs_used}"


def test_wordings_are_3_to_5_words_and_distinct_from_the_title(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)  # title: "Loop Engineering"

    thumb("order", "run", "srikar", "001")

    wordings = {read_meta(png)["wording"] for png in candidates(order_dir)}
    for wording in wordings:
        assert 3 <= len(wording.split()) <= 5, f"wording {wording!r} not 3-5 words"
        assert wording.lower() != "loop engineering", (
            "wording must be copywriting, not the video title"
        )
    # 3-5 proposals per Order, spread across the candidates
    assert 3 <= len(wordings) <= 5, f"expected 3-5 distinct wordings, got {sorted(wordings)}"


def test_background_prompts_carry_style_spec_language_and_restraint_rules(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)

    thumb("order", "run", "srikar", "001")

    # ground truth of what the provider actually received: the fake's journal
    journal_lines = (
        (thumb.root / ".thumb" / "provider-calls.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    received_prompts = [
        json.loads(line)["detail"]
        for line in journal_lines
        if json.loads(line)["method"] == "generate_background"
    ]

    for png in candidates(order_dir):
        meta = read_meta(png)
        prompt = meta["background_prompt"]
        spec = seed_spec(meta["style_spec"])

        # style-conditioned: the chosen spec's backdrop + palette language,
        # never assembled from the Brief alone
        assert spec["backdrop"] in prompt, (
            f"{png.name}: prompt lacks its spec's backdrop language\n{prompt}"
        )
        assert spec["accent"] in prompt, f"{png.name}: prompt lacks the accent color"

        # a deliberate Concept behind each candidate
        assert meta["concept"], f"{png.name} must record its Concept"
        assert meta["concept"] in prompt

        for rule in RESTRAINT_RULES:
            assert rule in prompt, f"{png.name}: prompt missing restraint rule {rule!r}"

        # the persisted prompt is the one the provider was really sent
        assert prompt in received_prompts


def test_text_device_matches_spec_and_text_box_respects_safe_margins(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)

    thumb("order", "run", "srikar", "001")

    SAFE = 64  # the hard safe margin — pinned here so it can never silently shrink
    for png in candidates(order_dir):
        meta = read_meta(png)
        spec = seed_spec(meta["style_spec"])

        assert meta["text_device"] == spec["text_device"], (
            f"{png.name}: device {meta.get('text_device')!r} but its spec "
            f"calls for {spec['text_device']!r}"
        )

        x, y, w, h = meta["layout_boxes"]["text"]
        assert w > 0 and h > 0
        assert x >= SAFE and y >= SAFE, f"{png.name}: text box {x, y, w, h} breaks margin"
        assert x + w <= 1280 - SAFE, f"{png.name}: text box {x, y, w, h} breaks right margin"
        assert y + h <= 720 - SAFE, f"{png.name}: text box {x, y, w, h} breaks bottom margin"


def test_composite_contains_the_subject_cutout_and_never_touches_the_source(thumb, make_photo):
    # An unmistakably green portrait: compositing can tint it ~15% and shadow
    # can darken the backdrop, but only the real cutout puts GREEN pixels in
    # the subject box.
    photos = thumb.root / "shoot"
    make_photo(photos / "face01.png", color=(60, 220, 60))
    thumb(
        "onboard", "srikar",
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
        "--photos", str(photos),
    )
    thumb(
        "order", "new", "srikar",
        "--title", "Loop Engineering",
        "--hook", "Why your loops fail and how to see it coming",
    )
    order_dir = thumb.root / "creators" / "srikar" / "orders" / "001"
    cutout = thumb.root / "creators" / "srikar" / "asset-pack" / "cutouts" / "face01.png"
    assert cutout.exists(), "onboarding (ticket 07) should have produced the cutout"
    cutout_bytes_before = cutout.read_bytes()

    thumb("order", "run", "srikar", "001")

    # ADR-0001: the Subject source is read-only — geometrically/photometrically
    # adjusted in the composite, never regenerated, never written back
    assert cutout.read_bytes() == cutout_bytes_before

    for png in candidates(order_dir):
        meta = read_meta(png)
        with Image.open(png) as composite:
            assert composite.size == (1280, 720)
            composite = composite.convert("RGB")

        # the background layer is persisted per candidate in the Order folder
        bg_path = order_dir / "backgrounds" / meta["background"]
        assert bg_path.exists(), f"{png.name}: background layer not persisted"

        # Subject cutout present: the center of the recorded subject box shows
        # the green portrait (a shadow or bare backdrop cannot be this green)
        x, y, w, h = meta["layout_boxes"]["subject"]
        cx, cy = x + w // 2, y + h // 2
        data = composite.crop((cx - 8, cy - 8, cx + 8, cy + 8)).tobytes()
        mean = [sum(data[i::3]) / (len(data) // 3) for i in range(3)]
        assert mean[1] > 120 and mean[1] > mean[0] + 30 and mean[1] > mean[2] + 30, (
            f"{png.name}: subject box center {mean} is not the green cutout"
        )


def test_missing_cutouts_surface_a_source_photo_limitation(thumb):
    # ADR-0001: identity is absolute — when no Asset Pack photo can serve the
    # Subject layer, the pipeline says so instead of degrading identity.
    # (Reaching this path at all now requires the explicit operator override —
    # by default a face-on creator with no cutouts refuses to run.)
    order_dir = start_order(thumb, make_photo=None)

    thumb("order", "run", "srikar", "001", "--allow-faceless-candidates")

    for png in candidates(order_dir):
        meta = read_meta(png)
        assert meta["source_photo"] is None
        assert meta["layout_boxes"]["subject"] is None
        assert "source-photo limitation" in meta["limitation"]
