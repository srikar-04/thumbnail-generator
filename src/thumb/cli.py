import argparse
import shutil
import sys
from pathlib import Path

from thumb import assetpack, library, pipeline, providers, sheet, workspace


def cmd_onboard(args):
    if args.face == "faceless":
        # ADR-0005: launch is face-only; this intake gate is the ONLY place
        # allowed to assume a face exists.
        print(
            "faceless creators are not yet supported (ADR-0005: face-only launch)",
            file=sys.stderr,
        )
        return 1
    cdir = workspace.creator_dir(args.root, args.creator)
    cdir.mkdir(parents=True, exist_ok=True)
    workspace.write_doc(
        workspace.creator_doc(args.root, args.creator),
        args.creator,
        {
            "Status": "onboarded",
            "Niche": args.niche,
            "Face": args.face,
            "Brand-Colors": args.brand_color,
        },
    )
    if args.photos:
        photo_dir = cdir / "asset-pack" / "photos"
        photo_dir.mkdir(parents=True, exist_ok=True)
        for src in sorted(Path(args.photos).iterdir()):
            if src.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                shutil.copy2(src, photo_dir / src.name)
        bound = providers.get_providers(args.root)
        analyzed = assetpack.analyze_photos(
            args.root, args.creator, bound.critique, bound.cutout
        )
        if analyzed:
            print(f"analyzed {len(analyzed)} photo(s)")
    if args.references:
        ref_dir = cdir / "asset-pack" / "references"
        ref_dir.mkdir(parents=True, exist_ok=True)
        for src in sorted(Path(args.references).iterdir()):
            if src.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                shutil.copy2(src, ref_dir / src.name)
    print(f"onboarded {args.creator}")
    return 0


def _require_creator(args):
    doc = workspace.creator_doc(args.root, args.creator)
    if not doc.exists():
        print(f"unknown creator: {args.creator} (run `thumb onboard` first)", file=sys.stderr)
        return None
    return doc


def cmd_order_new(args):
    if _require_creator(args) is None:
        return 1
    odir_parent = workspace.orders_dir(args.root, args.creator)
    odir_parent.mkdir(parents=True, exist_ok=True)
    existing = [p.name for p in odir_parent.iterdir() if p.is_dir() and p.name.isdigit()]
    order_id = f"{max((int(n) for n in existing), default=0) + 1:03d}"
    odir = workspace.order_dir(args.root, args.creator, order_id)
    odir.mkdir()
    workspace.write_doc(
        workspace.order_doc(args.root, args.creator, order_id),
        f"Order {order_id}",
        {
            "Status": "new",
            "Title": args.title,
            "Hook": args.hook,
        },
    )
    print(f"created order {order_id} for {args.creator}")
    return 0


def cmd_order_run(args):
    if _require_creator(args) is None:
        return 1
    order_doc = workspace.order_doc(args.root, args.creator, args.order)
    if not order_doc.exists():
        print(f"unknown order: {args.creator}/{args.order}", file=sys.stderr)
        return 1
    n = pipeline.run_order(
        args.root, args.creator, args.order, providers.get_providers(args.root), n=args.n
    )
    print(f"generated {n} candidates for {args.creator}/{args.order}")
    return 0


def cmd_order_sheet(args):
    if _require_creator(args) is None:
        return 1
    if not workspace.order_doc(args.root, args.creator, args.order).exists():
        print(f"unknown order: {args.creator}/{args.order}", file=sys.stderr)
        return 1
    out = sheet.write_sheet(args.root, args.creator, args.order)
    print(f"contact sheet: {out}")
    return 0


def cmd_order_list(args):
    croot = workspace.creators_root(args.root)
    if not croot.is_dir():
        print("no creators onboarded yet")
        return 0
    for creator in sorted(p.name for p in croot.iterdir() if p.is_dir()):
        odir = workspace.orders_dir(args.root, creator)
        if not odir.is_dir():
            continue
        for order_id in sorted(p.name for p in odir.iterdir() if p.is_dir()):
            fields = workspace.read_fields(workspace.order_doc(args.root, creator, order_id))
            print(
                f"{creator}/{order_id}  {fields.get('Status', '?'):<10}  "
                f"{fields.get('Title', '')}"
            )
    return 0


def cmd_style_add(args):
    reference = Path(args.reference)
    if not reference.exists():
        print(f"reference image not found: {reference}", file=sys.stderr)
        return 1
    if args.creator and _require_creator(args) is None:
        return 1
    bound = providers.get_providers(args.root)
    spec_path = library.add_spec(
        args.root, args.niche, reference, bound.critique, creator=args.creator
    )
    print(f"style spec: {spec_path}")
    return 0


def cmd_style_list(args):
    specs = library.list_specs(args.root, args.niche, creator=args.creator)
    if not specs:
        print(f"no style specs for niche {args.niche!r}")
        return 0
    for spec in specs:
        print(f"{spec['name']}  [{spec['text_device']}]  accent {spec['accent']}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="thumb")
    parser.add_argument("--root", default=".", help="workspace root (default: cwd)")
    sub = parser.add_subparsers(dest="command", required=True)

    onboard = sub.add_parser("onboard", help="create a Creator folder (Asset Pack home)")
    onboard.add_argument("creator", help="creator slug")
    onboard.add_argument("--niche", required=True)
    onboard.add_argument("--face", required=True, choices=["on", "faceless"])
    onboard.add_argument("--brand-color", required=True)
    onboard.add_argument("--photos", help="directory of face photos to copy into the Asset Pack")
    onboard.add_argument(
        "--references",
        help="directory of thumbnails the Creator admires (style sources, not face photos)",
    )
    onboard.set_defaults(func=cmd_onboard)

    style = sub.add_parser("style", help="Style Library: niche-keyed reference styles")
    style_sub = style.add_subparsers(dest="style_command", required=True)

    style_add = style_sub.add_parser("add", help="extract a style spec from a reference image")
    style_add.add_argument("reference", help="path to the reference thumbnail image")
    style_add.add_argument("--niche", required=True)
    style_add.add_argument(
        "--creator", help="scope the spec to this Creator's Asset Pack instead of the niche track"
    )
    style_add.set_defaults(func=cmd_style_add)

    style_list = style_sub.add_parser("list", help="list style specs available for a niche")
    style_list.add_argument("--niche", required=True)
    style_list.add_argument("--creator", help="also include this Creator's scoped specs")
    style_list.set_defaults(func=cmd_style_list)

    order = sub.add_parser("order", help="Order lifecycle: Brief in, Contact Sheet out")
    order_sub = order.add_subparsers(dest="order_command", required=True)

    order_new = order_sub.add_parser("new", help="start an Order from a Brief")
    order_new.add_argument("creator")
    order_new.add_argument("--title", required=True, help="video title")
    order_new.add_argument("--hook", required=True, help="2-3 sentences on the video's hook")
    order_new.set_defaults(func=cmd_order_new)

    order_run = order_sub.add_parser("run", help="generate Candidates for an Order")
    order_run.add_argument("creator")
    order_run.add_argument("order")
    order_run.add_argument("--n", type=int, default=20, help="number of candidates")
    order_run.set_defaults(func=cmd_order_run)

    order_sheet = order_sub.add_parser("sheet", help="write the Contact Sheet HTML")
    order_sheet.add_argument("creator")
    order_sheet.add_argument("order")
    order_sheet.set_defaults(func=cmd_order_sheet)

    order_list = order_sub.add_parser("list", help="list every Order and its Status")
    order_list.set_defaults(func=cmd_order_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
