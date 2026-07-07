import json
from pathlib import Path

SEED_DIR = Path(__file__).parent.parent / "src" / "thumb" / "styles"

# The launch schema (ticket 08 / PRD): every style spec carries these.
REQUIRED_FIELDS = {
    "name",
    "niche",
    "backdrop",
    "palette",
    "accent",
    "text_device",
    "icon_usage",
    "subject_treatment",
    "composition",
}
TEXT_DEVICES = {"chips", "label-bars", "plain-accent"}


def test_seeded_proven_directions_exist_and_are_well_formed():
    # The two operator-validated directions from the prototype ship as data.
    for name, device in (("black-editorial", "plain-accent"), ("red-chips", "chips")):
        spec = json.loads(
            (SEED_DIR / "tech-explainer" / f"{name}.json").read_text(encoding="utf-8")
        )
        assert REQUIRED_FIELDS <= set(spec)
        assert all(spec[field] for field in REQUIRED_FIELDS)
        assert spec["niche"] == "tech-explainer"
        assert spec["text_device"] == device
        assert spec["accent"].startswith("#") and len(spec["accent"]) == 7
        assert isinstance(spec["palette"], list) and spec["palette"]


def test_style_list_shows_seeded_specs_for_the_niche(thumb):
    out = thumb("style", "list", "--niche", "tech-explainer").stdout
    assert "black-editorial" in out
    assert "red-chips" in out


def test_style_add_extracts_a_niche_keyed_spec_from_a_reference(thumb, make_photo):
    # Filename tokens drive the fake VLM extractor (same convention as photo
    # analysis): grunge-wall backdrop, chips device, red accent.
    ref = thumb.root / "refs" / "ref-grunge-wall-chips-red.png"
    make_photo(ref, size=(1280, 720))

    thumb("style", "add", str(ref), "--niche", "tech-explainer")

    spec_path = (
        thumb.root / "style-library" / "tech-explainer" / "ref-grunge-wall-chips-red.json"
    )
    assert spec_path.exists()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    assert REQUIRED_FIELDS <= set(spec)
    assert all(spec[field] for field in REQUIRED_FIELDS)
    assert spec["niche"] == "tech-explainer"
    assert spec["text_device"] == "chips"
    assert spec["accent"] == "#D82C2C"
    assert "grunge wall" in spec["backdrop"]

    # the source reference is kept next to its spec
    assert (spec_path.parent / "ref-grunge-wall-chips-red.png").exists()

    # listing now returns seeds + the added spec
    out = thumb("style", "list", "--niche", "tech-explainer").stdout
    for name in ("black-editorial", "red-chips", "ref-grunge-wall-chips-red"):
        assert name in out


def test_creator_scoped_spec_lives_in_asset_pack_and_lists_with_niche_track(thumb, make_photo):
    thumb(
        "onboard", "srikar",
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
    )
    ref = thumb.root / "refs" / "ref-black-label-bars-yellow.png"
    make_photo(ref, size=(1280, 720))

    thumb("style", "add", str(ref), "--niche", "tech-explainer", "--creator", "srikar")

    scoped = (
        thumb.root / "creators" / "srikar" / "asset-pack" / "styles"
        / "ref-black-label-bars-yellow.json"
    )
    assert scoped.exists()
    spec = json.loads(scoped.read_text(encoding="utf-8"))
    assert spec["text_device"] == "label-bars"
    assert spec["accent"] == "#F2C200"

    # scoped spec is NOT on the shared niche track...
    niche_only = thumb("style", "list", "--niche", "tech-explainer").stdout
    assert "ref-black-label-bars-yellow" not in niche_only

    # ...but lists alongside it for that Creator
    with_creator = thumb(
        "style", "list", "--niche", "tech-explainer", "--creator", "srikar"
    ).stdout
    assert "ref-black-label-bars-yellow" in with_creator
    assert "black-editorial" in with_creator


def test_unknown_niche_lists_empty_and_a_new_niche_is_pure_data(thumb, make_photo):
    # ADR-0003: no niche branches in code — an unknown niche is empty, not an error.
    result = thumb("style", "list", "--niche", "cooking")
    assert "no style specs" in result.stdout

    # Adding a niche is data setup only: one style add, nothing else.
    ref = thumb.root / "refs" / "ref-paper-chips.png"
    make_photo(ref, size=(1280, 720))
    thumb("style", "add", str(ref), "--niche", "cooking")

    out = thumb("style", "list", "--niche", "cooking").stdout
    assert "ref-paper-chips" in out
    spec = json.loads(
        (thumb.root / "style-library" / "cooking" / "ref-paper-chips.json").read_text(
            encoding="utf-8"
        )
    )
    assert spec["niche"] == "cooking"


def test_hand_edited_spec_with_utf8_bom_still_loads(thumb, make_photo):
    # Windows editors save UTF-8 with a BOM; operator-edited specs must survive.
    ref = thumb.root / "refs" / "ref-black.png"
    make_photo(ref, size=(1280, 720))
    thumb("style", "add", str(ref), "--niche", "tech-explainer")

    spec_path = thumb.root / "style-library" / "tech-explainer" / "ref-black.json"
    spec_path.write_bytes(b"\xef\xbb\xbf" + spec_path.read_bytes())

    out = thumb("style", "list", "--niche", "tech-explainer").stdout
    assert "ref-black" in out
