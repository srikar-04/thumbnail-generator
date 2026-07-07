import json

from PIL import Image


def start_order(thumb, make_photo=None, creator="srikar"):
    args = [
        "onboard", creator,
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
    ]
    if make_photo is not None:
        photos = thumb.root / "shoot"
        make_photo(photos / "face01.png")
        args += ["--photos", str(photos)]
    thumb(*args)
    thumb(
        "order", "new", creator,
        "--title", "Loop Engineering",
        "--hook", "Why your loops fail and how to see it coming",
    )
    return thumb.root / "creators" / creator / "orders" / "001"


def test_order_run_produces_candidates_with_metadata(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)

    thumb("order", "run", "srikar", "001", "--n", "3")

    pngs = sorted((order_dir / "candidates").glob("*.png"))
    assert len(pngs) == 3
    for png in pngs:
        with Image.open(png) as image:
            assert image.size == (1280, 720)

        meta = json.loads(png.with_suffix(".json").read_text(encoding="utf-8"))
        assert meta["wording"]
        assert meta["source_photo"] == "face01.png"
        assert {"flip", "side", "scale", "crop"} <= set(meta["placement"])
        assert meta["layout_boxes"]["text"] is not None
        assert meta["layout_boxes"]["subject"] is not None

    assert "Status: generated" in (order_dir / "order.md").read_text(encoding="utf-8")


def test_order_run_without_photos_represents_subject_as_absent_layer(thumb):
    # ADR-0005: "no Subject" must be a representable state, not a crash.
    order_dir = start_order(thumb, make_photo=None)

    thumb("order", "run", "srikar", "001", "--n", "3")

    pngs = sorted((order_dir / "candidates").glob("*.png"))
    assert len(pngs) == 3
    meta = json.loads(pngs[0].with_suffix(".json").read_text(encoding="utf-8"))
    assert meta["source_photo"] is None
    assert meta["layout_boxes"]["subject"] is None
