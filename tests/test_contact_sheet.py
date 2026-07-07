import json
import re

from test_order_run import start_order


def test_sheet_is_self_contained_html_referencing_every_candidate(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)
    thumb("order", "run", "srikar", "001")

    thumb("order", "sheet", "srikar", "001")

    sheet = order_dir / "contact_sheet.html"
    assert sheet.exists()
    html = sheet.read_text(encoding="utf-8")

    candidates = sorted((order_dir / "candidates").glob("*.png"))
    assert candidates
    for png in candidates:
        assert f"candidates/{png.name}" in html
        wording = json.loads(png.with_suffix(".json").read_text(encoding="utf-8"))["wording"]
        assert wording in html

    # self-contained: openable from disk, no external resources (strict CSP world)
    assert not re.search(r"(src|href)=[\"']https?://", html)
    assert "Loop Engineering" in html  # order context visible to the operator
