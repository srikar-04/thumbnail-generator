"""Contact Sheet: static, self-contained HTML grid of an Order's Candidates
(ADR-0004 — the browser is the image viewer; no server, no external resources)."""

import html
import json

from thumb import workspace

PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Contact Sheet — {creator} / order {order_id}</title>
<style>
body {{ font-family: sans-serif; background: #1a1a1a; color: #eee; margin: 2rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1.5rem; }}
figure {{ margin: 0; }}
img {{ width: 100%; border-radius: 4px; }}
figcaption {{ font-size: 0.85rem; padding-top: 0.4rem; color: #bbb; }}
</style>
</head>
<body>
<h1>{creator} / order {order_id} — {title}</h1>
<p>Status: {status}</p>
<div class="grid">
{figures}
</div>
</body>
</html>
"""

FIGURE = """<figure>
<img src="candidates/{name}" alt="{wording}">
<figcaption><strong>{wording}</strong> — {name}</figcaption>
</figure>"""


def write_sheet(root, creator, order_id):
    odir = workspace.order_dir(root, creator, order_id)
    brief = workspace.read_fields(workspace.order_doc(root, creator, order_id))

    figures = []
    for png in sorted((odir / "candidates").glob("*.png")):
        meta = json.loads(png.with_suffix(".json").read_text(encoding="utf-8"))
        figures.append(
            FIGURE.format(name=html.escape(png.name), wording=html.escape(meta["wording"]))
        )

    out = odir / "contact_sheet.html"
    out.write_text(
        PAGE.format(
            creator=html.escape(creator),
            order_id=html.escape(order_id),
            title=html.escape(brief.get("Title", "")),
            status=html.escape(brief.get("Status", "")),
            figures="\n".join(figures),
        ),
        encoding="utf-8",
    )
    return out
