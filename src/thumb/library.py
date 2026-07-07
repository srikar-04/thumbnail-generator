"""Style Library: niche-keyed style specs (ADR-0003 — niche taste is data).

Three spec sources, merged at read time:
- seeds shipped with the package (the proven directions),
- workspace additions under `style-library/<niche>/`,
- Creator-scoped specs inside an Asset Pack.

Every spec read is validated against the launch schema; a spec that fails
validation is a loud error, never silently skipped.
"""

import json
import shutil
from importlib import resources
from pathlib import Path

from thumb import workspace

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


def validate(spec, source):
    missing = REQUIRED_FIELDS - set(spec)
    if missing:
        raise SystemExit(f"invalid style spec {source}: missing {sorted(missing)}")
    empty = [field for field in REQUIRED_FIELDS if not spec[field]]
    if empty:
        raise SystemExit(f"invalid style spec {source}: empty {empty}")
    if spec["text_device"] not in TEXT_DEVICES:
        raise SystemExit(
            f"invalid style spec {source}: text_device {spec['text_device']!r} "
            f"not one of {sorted(TEXT_DEVICES)}"
        )
    return spec


def library_dir(root, niche):
    return Path(root) / "style-library" / niche


def _load(path_or_traversable, source):
    # utf-8-sig: operator-edited specs saved by Windows editors carry a BOM
    spec = json.loads(path_or_traversable.read_text(encoding="utf-8-sig"))
    return validate(spec, source)


def add_spec(root, niche, reference_path, vlm, creator=None):
    """Extract a style spec from a reference image and store it niche-keyed
    (or Creator-scoped inside their Asset Pack), reference image alongside."""
    reference = Path(reference_path)
    spec = vlm.extract_style_spec(reference)
    spec["name"] = reference.stem
    spec["niche"] = niche
    validate(spec, str(reference))

    if creator is not None:
        target_dir = workspace.creator_dir(root, creator) / "asset-pack" / "styles"
    else:
        target_dir = library_dir(root, niche)
    target_dir.mkdir(parents=True, exist_ok=True)

    spec_path = target_dir / f"{reference.stem}.json"
    spec_path.write_text(
        json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    shutil.copy2(reference, target_dir / reference.name)
    return spec_path


def list_specs(root, niche, creator=None):
    """All specs available for a niche: seeds + workspace + Creator-scoped."""
    specs = []

    seed_dir = resources.files("thumb") / "styles" / niche
    if seed_dir.is_dir():
        for entry in sorted(seed_dir.iterdir(), key=lambda e: e.name):
            if entry.name.endswith(".json"):
                specs.append(_load(entry, f"seed {niche}/{entry.name}"))

    workspace_dir = library_dir(root, niche)
    if workspace_dir.is_dir():
        for path in sorted(workspace_dir.glob("*.json")):
            specs.append(_load(path, str(path)))

    if creator is not None:
        creator_dir = workspace.creator_dir(root, creator) / "asset-pack" / "styles"
        if creator_dir.is_dir():
            for path in sorted(creator_dir.glob("*.json")):
                specs.append(_load(path, str(path)))

    return specs
