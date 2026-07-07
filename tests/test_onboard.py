def test_onboard_creates_creator_folder_with_recorded_fields(thumb):
    thumb(
        "onboard", "srikar",
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
    )

    creator_md = thumb.root / "creators" / "srikar" / "creator.md"
    assert creator_md.exists()
    text = creator_md.read_text(encoding="utf-8")
    assert "Status: onboarded" in text
    assert "Niche: tech-explainer" in text
    assert "Face: on" in text
    assert "Brand-Colors: #D82C2C" in text


def test_faceless_onboard_rejected_with_no_half_written_folder(thumb):
    result = thumb(
        "onboard", "ghost",
        "--niche", "tech-explainer",
        "--face", "faceless",
        "--brand-color", "#000000",
        check=False,
    )

    assert result.returncode != 0
    assert "not yet supported" in (result.stdout + result.stderr)
    assert not (thumb.root / "creators" / "ghost").exists()
