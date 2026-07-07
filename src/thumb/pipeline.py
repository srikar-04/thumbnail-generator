"""Order pipeline: Brief -> Wording -> Background -> composite -> Candidates.

Walking-skeleton version: placeholder quality on purpose. Placement is a fixed
rule (ticket 02 upgrades it), compositing is a naive paste (ticket 09 brings the
real recipe). The shapes that matter — candidate files + metadata alongside,
Subject as an optional layer, Status transitions — are the real ones.
"""

import json

from PIL import Image, ImageDraw, ImageFont

from thumb import workspace

CANVAS = (1280, 720)
SAFE_MARGIN = 64


def _asset_photos(root, creator):
    photos_dir = workspace.creator_dir(root, creator) / "asset-pack" / "photos"
    if not photos_dir.is_dir():
        return []
    return sorted(p for p in photos_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"})


def _compose(background, photo_path, wording):
    """Naive composite; returns (image, placement, layout_boxes)."""
    canvas = background.resize(CANVAS)

    placement = {"flip": False, "side": "right", "scale": 0.6, "crop": "full"}
    subject_box = None
    if photo_path is not None:
        with Image.open(photo_path) as photo:
            target_h = int(CANVAS[1] * placement["scale"])
            target_w = int(photo.width * target_h / photo.height)
            subject = photo.resize((target_w, target_h))
        x = CANVAS[0] - target_w - SAFE_MARGIN
        y = CANVAS[1] - target_h
        canvas.paste(subject, (x, y))
        subject_box = [x, y, target_w, target_h]

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=64)
    text_xy = (SAFE_MARGIN, SAFE_MARGIN)
    bbox = draw.textbbox(text_xy, wording, font=font)
    draw.text(text_xy, wording, font=font, fill=(255, 255, 255))
    text_box = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]

    return canvas, placement, {"text": text_box, "subject": subject_box}


def run_order(root, creator, order_id, providers, n=3):
    order_doc = workspace.order_doc(root, creator, order_id)
    brief = workspace.read_fields(order_doc)
    photos = _asset_photos(root, creator)
    photo = photos[0] if photos else None

    wordings = providers.wording.propose_wordings(brief["Title"], brief["Hook"], n)

    cand_dir = workspace.order_dir(root, creator, order_id) / "candidates"
    cand_dir.mkdir(exist_ok=True)
    for i in range(n):
        wording = wordings[i % len(wordings)]
        prompt = f"background for '{brief['Title']}' — variant {i + 1}"
        background = providers.background.generate_background(prompt, CANVAS)
        canvas, placement, layout_boxes = _compose(background, photo, wording)

        stem = cand_dir / f"cand-{i + 1:02d}"
        canvas.save(stem.with_suffix(".png"))
        metadata = {
            "wording": wording,
            "source_photo": photo.name if photo else None,
            "background_prompt": prompt,
            "placement": placement,
            "layout_boxes": layout_boxes,
            "style_spec": None,  # arrives with the Style Library (ticket 08)
        }
        stem.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    workspace.set_field(order_doc, "Status", "generated")
    return n
