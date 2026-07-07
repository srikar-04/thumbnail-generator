def onboard_creator(thumb, slug="srikar"):
    thumb(
        "onboard", slug,
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
    )
    return slug


def test_order_new_creates_order_folder_with_brief_and_status(thumb):
    onboard_creator(thumb)

    result = thumb(
        "order", "new", "srikar",
        "--title", "Loop Engineering",
        "--hook", "Why your loops fail and how to see it coming",
    )

    order_md = thumb.root / "creators" / "srikar" / "orders" / "001" / "order.md"
    assert order_md.exists()
    text = order_md.read_text(encoding="utf-8")
    assert "Status: new" in text
    assert "Title: Loop Engineering" in text
    assert "Hook: Why your loops fail and how to see it coming" in text
    assert "001" in result.stdout


def test_order_new_for_unknown_creator_fails(thumb):
    result = thumb(
        "order", "new", "nobody",
        "--title", "x", "--hook", "y",
        check=False,
    )
    assert result.returncode != 0
    assert not (thumb.root / "creators" / "nobody").exists()
