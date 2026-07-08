from test_order_run import start_order


def snapshot(order_dir):
    # order.md mutates (Status:) and ledger.jsonl is an append-only account of
    # real spend — a re-run genuinely spends again, so it may never be reset to
    # look deterministic. Everything generated must be byte-identical.
    files = sorted(
        p
        for p in order_dir.rglob("*")
        if p.is_file() and p.name not in ("order.md", "ledger.jsonl")
    )
    return {p.relative_to(order_dir).as_posix(): p.read_bytes() for p in files}


def test_rerunning_an_order_on_fake_providers_is_byte_identical(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)

    thumb("order", "run", "srikar", "001")
    thumb("order", "sheet", "srikar", "001")
    first = snapshot(order_dir)

    thumb("order", "run", "srikar", "001")
    thumb("order", "sheet", "srikar", "001")
    second = snapshot(order_dir)

    assert first.keys() == second.keys()
    assert all(first[name] == second[name] for name in first), (
        "fake-provider runs must be deterministic; differing files: "
        + ", ".join(name for name in first if first[name] != second[name])
    )
