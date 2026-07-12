"""Capture checklist: acceptance rules run against Asset Pack photos.

The single source of the checklist is `capture-guide.md` (the page sent to
Creators) — its `[check: ...]` / `[check-set: ...]` tokens are parsed into the
rules evaluated here, over cached photo metadata. No VLM calls happen here.

Token grammar:
    [check: <field> = <value>]        per-photo: metadata[field] must equal value
    [check-set: <id> >= <n>]          set-level minimum
    [check-set: <id> <low>-<high>]    set-level count range
"""

import re
from functools import cache
from importlib import resources

# a rule's reason may wrap onto indented continuation lines — capture them all
_PHOTO_RE = re.compile(r"\[check:\s*([a-z-]+)\s*=\s*([a-z]+)\]\s*(.+(?:\n[ \t]+\S.*)*)")
_SET_MIN_RE = re.compile(r"\[check-set:\s*([a-z-]+)\s*>=\s*(\d+)\]")
_SET_RANGE_RE = re.compile(r"\[check-set:\s*([a-z-]+)\s+(\d+)-(\d+)\]")


def guide_text():
    return (resources.files("thumb") / "capture-guide.md").read_text(encoding="utf-8")


@cache
def load():
    """Parse the guide into (photo_checks, set_minimums, set_ranges)."""
    text = guide_text()
    photo_checks = [
        (field, {"false": False, "true": True}.get(value, value), " ".join(reason.split()))
        for field, value, reason in _PHOTO_RE.findall(text)
    ]
    set_minimums = {check_id: int(n) for check_id, n in _SET_MIN_RE.findall(text)}
    set_ranges = {
        check_id: (int(low), int(high))
        for check_id, low, high in _SET_RANGE_RE.findall(text)
    }
    return photo_checks, set_minimums, set_ranges


def evaluated_item_ids():
    photo_checks, set_minimums, set_ranges = load()
    return [field for field, _, _ in photo_checks] + list(set_minimums) + list(set_ranges)


def evaluate_photo(metadata):
    """Return rejection reasons for one photo ([] means accepted)."""
    photo_checks, _, _ = load()
    return [
        f"{field}: {reason}"
        for field, wanted, reason in photo_checks
        if metadata.get(field) != wanted
    ]


def evaluate_set(accepted_metadata):
    """Return (check_id, ok, detail) for checks that judge the whole photo set."""
    _, set_minimums, set_ranges = load()
    results = []

    minimum = set_minimums["expression-variety"]
    expressions = sorted({m["expression"] for m in accepted_metadata})
    results.append(
        (
            "expression-variety",
            len(expressions) >= minimum,
            f"{len(expressions)} distinct expression(s) among accepted photos "
            f"({', '.join(expressions) or 'none'}), want >= {minimum}",
        )
    )

    low, high = set_ranges["photo-count"]
    count = len(accepted_metadata)
    results.append(
        (
            "photo-count",
            low <= count <= high,
            f"{count} accepted photo(s), guide recommends {low}-{high}",
        )
    )
    return results
