import json
import re
from pathlib import Path

CAPTURE_GUIDE = Path(__file__).parent.parent / "src" / "thumb" / "capture-guide.md"


def provider_calls(root, method):
    """Fake providers journal every call to disk; count entries for a method."""
    log = root / ".thumb" / "provider-calls.jsonl"
    if not log.exists():
        return 0
    return sum(
        1
        for line in log.read_text(encoding="utf-8").splitlines()
        if json.loads(line)["method"] == method
    )


def onboard_with_photos(thumb, make_photo, names, extra=(), creator="srikar", check=True):
    shoot = thumb.root / "shoot"
    for name in names:
        make_photo(shoot / name)
    result = thumb(
        "onboard", creator,
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
        "--photos", str(shoot),
        *extra,
        check=check,
    )
    return thumb.root / "creators" / creator / "asset-pack", result


def test_onboard_caches_photo_analysis_metadata_per_photo(thumb, make_photo):
    # Filename tokens drive the fake VLM's deterministic analysis.
    pack, _ = onboard_with_photos(
        thumb, make_photo,
        ["face-point-left-shock.png", "face-plain.png"],
    )

    meta = json.loads(
        (pack / "photos" / "face-point-left-shock.json").read_text(encoding="utf-8")
    )
    assert meta["gesture"] == "point-left"
    assert meta["expression"] == "shock"
    assert meta["gaze"] == "camera"
    assert meta["clothing_text"] is False
    assert meta["crops"], "viable crops must be a non-empty list"

    meta2 = json.loads((pack / "photos" / "face-plain.json").read_text(encoding="utf-8"))
    assert meta2["gesture"] == "none"
    assert meta2["expression"] == "neutral"


def test_onboard_generates_cutouts_with_transparency(thumb, make_photo):
    from PIL import Image

    pack, _ = onboard_with_photos(thumb, make_photo, ["face-shock.png", "face-joy.png"])

    for name in ("face-shock.png", "face-joy.png"):
        cutout = pack / "cutouts" / name
        assert cutout.exists()
        with Image.open(cutout) as image:
            assert image.mode == "RGBA"
            width, height = image.size
            assert image.getpixel((0, 0))[3] == 0, "corner must be transparent"
            assert image.getpixel((width // 2, height // 2))[3] == 255, (
                "subject center must be opaque"
            )


def test_checklist_rejects_failing_photos_with_reasons_in_report(thumb, make_photo):
    pack, _ = onboard_with_photos(
        thumb, make_photo,
        [
            "face-flat.png",        # flat lighting -> reject
            "face-busy-joy.png",    # busy background -> reject
            "face-filtered.png",    # beauty filter -> reject
            "face-shock.png",       # clean -> accept
        ],
    )

    report = (pack / "onboarding-report.md").read_text(encoding="utf-8")

    assert "face-flat.png" in report and "lighting" in report
    assert "face-busy-joy.png" in report and "background" in report
    assert "face-filtered.png" in report and "filter" in report

    # rejected photos get no cutout (analysis stays cached so re-runs don't re-pay)
    for name in ("face-flat", "face-busy-joy", "face-filtered"):
        assert not (pack / "cutouts" / f"{name}.png").exists()

    # the clean photo is accepted and fully processed
    assert "face-shock.png" in report
    assert (pack / "photos" / "face-shock.json").exists()
    assert (pack / "cutouts" / "face-shock.png").exists()


def test_rejection_reasons_carry_the_guides_full_sentence_not_a_truncated_line(thumb, make_photo):
    # Milestone-run regression (2026-07-08): the guide's rules wrap across
    # lines, and the report quoted only the first line — "…window light or"
    # read as garbage and hid WHY the photo failed.
    pack, _ = onboard_with_photos(thumb, make_photo, ["face-flat.png"], check=False)

    report = (pack / "onboarding-report.md").read_text(encoding="utf-8")
    assert "window light or a single lamp at roughly 45" in report, (
        "the lighting rule's continuation line must survive into the report"
    )
    assert not re.search(r"window light or\s*$", report, re.MULTILINE), (
        "no reason may end mid-sentence at the guide's line wrap"
    )


def test_neutral_only_photo_set_produces_readable_set_failure(thumb, make_photo):
    pack, _ = onboard_with_photos(
        thumb, make_photo,
        ["face-a.png", "face-b.png", "face-c.png"],  # all default to neutral
    )

    report = (pack / "onboarding-report.md").read_text(encoding="utf-8")
    assert "expression-variety: FAIL" in report
    assert "Status: attention-needed" in report


def test_varied_expression_set_passes_set_checks(thumb, make_photo):
    pack, _ = onboard_with_photos(
        thumb, make_photo,
        ["face-shock.png", "face-grimace.png", "face-joy.png", "face-point-left-curious.png"],
    )

    report = (pack / "onboarding-report.md").read_text(encoding="utf-8")
    assert "expression-variety: ok" in report


def test_onboard_surfaces_acceptance_counts_and_points_at_the_report(thumb, make_photo):
    _, result = onboard_with_photos(
        thumb, make_photo, ["face-shock.png", "face-flat.png"]
    )

    out = result.stdout + result.stderr
    assert "accepted 1" in out and "rejected 1" in out, (
        "the operator must see the checklist verdict without opening the report"
    )
    assert "onboarding-report.md" in out


def test_onboard_fails_loudly_when_no_photo_survives_the_checklist(thumb, make_photo):
    # Milestone-run regression (2026-07-08): all 11 real photos were rejected
    # and onboard still printed plain success — the operator only found out
    # after spending credits on a faceless order.
    _, result = onboard_with_photos(
        thumb, make_photo, ["face-flat.png", "face-busy-flat.png"], check=False
    )

    assert result.returncode != 0
    assert "no photos accepted" in result.stderr
    assert "onboarding-report.md" in result.stderr


def test_capture_guide_exists_and_is_the_checklist_source(thumb, make_photo):
    # The one-page guide sent to every Creator lives in the repo...
    assert CAPTURE_GUIDE.exists()
    guide = CAPTURE_GUIDE.read_text(encoding="utf-8")
    guide_ids = set(re.findall(r"\[check(?:-set)?:\s*([a-z-]+)", guide))
    assert guide_ids, "guide must declare machine-readable checklist items"

    # ...and the onboard command evaluates exactly those items, no other source.
    pack, _ = onboard_with_photos(thumb, make_photo, ["face-shock.png"])
    report = (pack / "onboarding-report.md").read_text(encoding="utf-8")
    evaluated = set(re.findall(r"^- evaluated: ([a-z-]+)$", report, re.MULTILINE))
    assert evaluated == guide_ids


def test_rerunning_onboard_reanalyzes_and_recuts_nothing(thumb, make_photo):
    pack, _ = onboard_with_photos(
        thumb, make_photo, ["face-shock.png", "face-grimace.png"]
    )
    assert provider_calls(thumb.root, "analyze_photo") == 2
    cutout_before = (pack / "cutouts" / "face-shock.png").read_bytes()

    thumb(
        "onboard", "srikar",
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
        "--photos", str(thumb.root / "shoot"),
    )

    assert provider_calls(thumb.root, "analyze_photo") == 2, (
        "second onboard must not re-pay VLM analysis for cached photos"
    )
    assert (pack / "cutouts" / "face-shock.png").read_bytes() == cutout_before


def test_onboard_records_creator_style_references(thumb, make_photo):
    refs = thumb.root / "admired"
    make_photo(refs / "ref-mrwhosetheboss.png", size=(1280, 720))
    make_photo(refs / "ref-fireship.jpg", size=(1280, 720))

    pack, _ = onboard_with_photos(
        thumb, make_photo, ["face-shock.png"],
        extra=("--references", str(refs)),
    )

    assert (pack / "references" / "ref-mrwhosetheboss.png").exists()
    assert (pack / "references" / "ref-fireship.jpg").exists()
    # references are style sources, not face photos: no analysis, no cutouts
    assert not (pack / "cutouts" / "ref-mrwhosetheboss.png").exists()


def test_order_run_makes_zero_photo_analysis_calls(thumb, make_photo):
    # All photo analysis is cached at onboarding (issue 02); an Order must
    # never re-pay it.
    onboard_with_photos(thumb, make_photo, ["face-shock.png", "face-point-left-joy.png"])
    calls_after_onboard = provider_calls(thumb.root, "analyze_photo")
    assert calls_after_onboard == 2

    thumb(
        "order", "new", "srikar",
        "--title", "Loop Engineering",
        "--hook", "Why your loops fail",
    )
    thumb("order", "run", "srikar", "001")

    assert provider_calls(thumb.root, "analyze_photo") == calls_after_onboard
