from test_order_run import start_order


def test_order_list_shows_orders_with_status(thumb, make_photo):
    start_order(thumb, make_photo)
    thumb(
        "order", "new", "srikar",
        "--title", "Second Video",
        "--hook", "another hook",
    )
    thumb("order", "run", "srikar", "001")

    out = thumb("order", "list").stdout

    lines = [line for line in out.splitlines() if line.strip()]
    line_001 = next(line for line in lines if "001" in line)
    line_002 = next(line for line in lines if "002" in line)
    assert "srikar" in line_001 and "generated" in line_001 and "Loop Engineering" in line_001
    assert "srikar" in line_002 and "new" in line_002 and "Second Video" in line_002
