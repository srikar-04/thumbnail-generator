"""Order pipeline: Brief -> Wording/Concepts -> style-conditioned Backgrounds ->
compositor recipe -> Candidates.

Placement is still the skeleton's fixed rule (flip only when it says so; ticket
02 brings content-aware decisions). Every stage output lands in the Order
folder so it is observable at the disk seam and reusable by Revisions.
"""

import json

from thumb import compositor, library, workspace

CANVAS = compositor.CANVAS
SAFE_MARGIN = compositor.SAFE_MARGIN
SPECS_PER_ORDER = 3  # spread Candidates across 2-3 directions (PRD story 12)
WORDINGS_PER_ORDER = 4  # 3-5 proposals per Order (PRD story 16)
CONCEPTS_PER_SPEC = 3

# The prototype's single biggest quality lever: restrained, flat-graphic
# backdrops instead of the model's default cinematic scenes.
RESTRAINT_RULES = (
    "one focal element, generous negative space, one accent color, "
    "no clutter, no dense texture, no busy patterns"
)


def _background_prompt(spec, concept):
    palette = ", ".join(spec["palette"])
    return (
        f"Flat graphic YouTube thumbnail backdrop, 16:9. {spec['backdrop']}. "
        f"Palette {palette}, accent {spec['accent']}. {concept}. "
        f"{RESTRAINT_RULES}. "
        f"No people, no faces, no text, no letters, no logos."
    )


def _asset_photos(root, creator):
    photos_dir = workspace.creator_dir(root, creator) / "asset-pack" / "photos"
    if not photos_dir.is_dir():
        return []
    return sorted(p for p in photos_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"})


def _cutouts(root, creator):
    cutouts_dir = workspace.creator_dir(root, creator) / "asset-pack" / "cutouts"
    if not cutouts_dir.is_dir():
        return []
    return sorted(cutouts_dir.glob("*.png"))


def run_order(root, creator, order_id, providers, n=20, allow_faceless=False):
    order_doc = workspace.order_doc(root, creator, order_id)
    brief = workspace.read_fields(order_doc)
    creator_fields = workspace.read_fields(workspace.creator_doc(root, creator))
    niche = creator_fields["Niche"]
    specs = library.list_specs(root, niche, creator=creator)[:SPECS_PER_ORDER]
    if not specs:
        raise SystemExit(
            f"no style specs for niche {niche!r} — seed the Style Library first"
        )
    photo_names = {p.stem: p.name for p in _asset_photos(root, creator)}
    cutouts = _cutouts(root, creator)
    if creator_fields.get("Face") == "on" and not cutouts and not allow_faceless:
        # gate BEFORE any provider call: a face-on Order with no cutouts can
        # only produce faceless, unsellable candidates — refuse to spend
        report = workspace.creator_dir(root, creator) / "asset-pack" / "onboarding-report.md"
        raise SystemExit(
            f"refusing to run: {creator!r} is a face-on creator but the Asset "
            f"Pack has no cutouts, so every candidate would come out faceless. "
            f"See {report} (capture-checklist rejections?) and re-onboard with "
            f"usable photos — or pass --allow-faceless-candidates to spend on "
            f"this deliberately."
        )

    wordings = providers.wording.propose_wordings(
        brief["Title"], brief["Hook"], WORDINGS_PER_ORDER
    )
    concepts = {
        spec["name"]: providers.wording.propose_concepts(
            brief["Title"], brief["Hook"], spec["backdrop"], CONCEPTS_PER_SPEC
        )
        for spec in specs
    }

    order_dir = workspace.order_dir(root, creator, order_id)
    bg_dir = order_dir / "backgrounds"
    cand_dir = order_dir / "candidates"
    bg_dir.mkdir(exist_ok=True)
    cand_dir.mkdir(exist_ok=True)
    for i in range(n):
        spec = specs[i % len(specs)]
        wording = wordings[i % len(wordings)]
        spec_concepts = concepts[spec["name"]]
        concept = spec_concepts[(i // len(specs)) % len(spec_concepts)]
        cutout = cutouts[i % len(cutouts)] if cutouts else None

        prompt = _background_prompt(spec, concept)
        background = providers.background.generate_background(prompt, CANVAS)
        bg_name = f"bg-{i + 1:02d}.png"
        background.save(bg_dir / bg_name)

        # the skeleton placement rule — flip only when this decision says so
        # (always False until ticket 02's content-aware logic)
        placement = {"flip": False, "side": "right", "scale": 0.88, "crop": "full"}
        canvas, layout_boxes = compositor.compose(
            background, cutout, wording, spec, placement
        )

        stem = cand_dir / f"cand-{i + 1:02d}"
        canvas.save(stem.with_suffix(".png"))
        metadata = {
            "wording": wording,
            "concept": concept,
            "source_photo": photo_names.get(cutout.stem, cutout.name) if cutout else None,
            "background": bg_name,
            "background_prompt": prompt,
            "placement": placement,
            "layout_boxes": layout_boxes,
            "style_spec": spec["name"],
            "text_device": spec["text_device"],
            "cost_usd": 0.0,  # fakes are free; the real ledger lands with ticket 10
            # ADR-0001: when no photo can serve the Subject, say so — never
            # regenerate or repaint identity to fill the gap
            "limitation": None if cutout else (
                "source-photo limitation: no Asset Pack cutout available for this Concept"
            ),
        }
        stem.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    workspace.set_field(order_doc, "Status", "generated")
    return n
