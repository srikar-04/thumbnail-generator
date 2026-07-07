"""Asset Pack intake: analyze photos once at onboarding, cache the metadata.

Per-Order placement (ticket 02) reads these cached records — photo analysis
never happens during `order run`.
"""

import json

from thumb import checklist, workspace

PHOTO_SUFFIXES = {".png", ".jpg", ".jpeg"}


def photos_dir(root, creator):
    return workspace.creator_dir(root, creator) / "asset-pack" / "photos"


def photo_metadata_path(photo_path):
    return photo_path.with_suffix(".json")


def cutouts_dir(root, creator):
    return workspace.creator_dir(root, creator) / "asset-pack" / "cutouts"


def analyze_photos(root, creator, vlm, cutout_engine):
    """Analyze, checklist-evaluate, and cut every Asset Pack photo; cache all
    of it and write the onboarding report."""
    pdir = photos_dir(root, creator)
    if not pdir.is_dir():
        return []

    cdir = cutouts_dir(root, creator)
    analyzed, accepted, rejected = [], [], []
    for photo in sorted(p for p in pdir.iterdir() if p.suffix.lower() in PHOTO_SUFFIXES):
        meta_path = photo_metadata_path(photo)
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        else:
            metadata = vlm.analyze_photo(photo)
            meta_path.write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            analyzed.append(photo.name)

        reasons = checklist.evaluate_photo(metadata)
        if reasons:
            rejected.append((photo.name, reasons))
            continue
        accepted.append((photo.name, metadata))
        cutout_path = cdir / f"{photo.stem}.png"
        if not cutout_path.exists():
            cdir.mkdir(parents=True, exist_ok=True)
            cutout_engine.cut(photo).save(cutout_path)

    set_results = checklist.evaluate_set([m for _, m in accepted])
    _write_report(root, creator, accepted, rejected, set_results)
    return analyzed


def _write_report(root, creator, accepted, rejected, set_results):
    ok = not rejected and all(passed for _, passed, _ in set_results)
    lines = [
        f"# Onboarding report — {creator}",
        "",
        f"Status: {'ok' if ok else 'attention-needed'}",
        "",
        "## Photos",
        "",
    ]
    for name, reasons in rejected:
        lines.append(f"- {name}: REJECTED — {'; '.join(reasons)}")
    for name, _ in accepted:
        lines.append(f"- {name}: accepted")
    lines += ["", "## Set checks", ""]
    for check_id, passed, detail in set_results:
        lines.append(f"- {check_id}: {'ok' if passed else 'FAIL'} — {detail}")
    lines += ["", "## Checklist evaluated (source: capture-guide.md)", ""]
    for item_id in checklist.evaluated_item_ids():
        lines.append(f"- evaluated: {item_id}")
    report_path = workspace.creator_dir(root, creator) / "asset-pack" / "onboarding-report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
