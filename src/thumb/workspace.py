"""Plain-file conventions (ADR-0004): Creators are folders, Orders are folders,
state is `Key: value` lines in markdown docs."""

from pathlib import Path


def creators_root(root):
    return Path(root) / "creators"


def creator_dir(root, slug):
    return creators_root(root) / slug


def creator_doc(root, slug):
    return creator_dir(root, slug) / "creator.md"


def orders_dir(root, slug):
    return creator_dir(root, slug) / "orders"


def order_dir(root, slug, order_id):
    return orders_dir(root, slug) / order_id


def order_doc(root, slug, order_id):
    return order_dir(root, slug, order_id) / "order.md"


def write_doc(path, title, fields):
    lines = [f"# {title}", ""]
    lines += [f"{key}: {value}" for key, value in fields.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_fields(path):
    fields = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if ": " in line and not line.startswith("#"):
            key, value = line.split(": ", 1)
            fields[key] = value
    return fields


def set_field(path, key, value):
    fields = read_fields(path)
    title = Path(path).read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
    fields[key] = value
    write_doc(path, title, fields)
