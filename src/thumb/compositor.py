"""Compositor: the prototype's validated recipe, absorbed as the launch baseline.

Everything here is deterministic Pillow work. The Subject is only ever
geometrically and photometrically adjusted — never AI-regenerated (ADR-0001).
Text is rendered programmatically with real fonts, per the style spec's device.
"""

from pathlib import Path

from PIL import (Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)

CANVAS = (1280, 720)
SAFE_MARGIN = 64
EDGE_BLEED = 20  # the subject bleeds slightly off-frame so the crop feels intentional
LINE_GAP = 8
CHIP_PAD = (30, 20)  # horizontal, vertical padding inside a chip/bar
FIT_PAD = 70  # width headroom so chip padding + rotation never overflow the zone

CHIP_PAPER = (250, 247, 240)  # torn-paper white
INK = (20, 20, 20)
BAR_BLACK = (16, 16, 16)
WHITE = (255, 255, 255)


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _find_font():
    for name in ("impact.ttf", "arialbd.ttf", "arial.ttf"):
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return str(path)
    return None


_FONT_PATH = _find_font()


def _font(size):
    if _FONT_PATH:
        return ImageFont.truetype(_FONT_PATH, size)
    return ImageFont.load_default(size)


def bg_palette(bg):
    """(mean_color, rim_color) sampled from the background."""
    small = bg.resize((64, 36))
    data = small.convert("RGB").tobytes()
    px = list(zip(data[0::3], data[1::3], data[2::3]))
    mean = tuple(sum(c[i] for c in px) // len(px) for i in range(3))
    accent = max(px, key=lambda c: (max(c) - min(c)) * max(c))  # bright + saturated
    # lift toward white so the rim reads as light, not paint
    accent = tuple(min(255, int(a * 0.6 + 255 * 0.4)) for a in accent)
    return mean, accent


def _trimmed_span(histogram, cutoff_frac=0.01):
    """Widest per-channel value span after trimming 1% tails — the dynamic
    range autocontrast would actually operate on."""
    widest = 0
    for start in (0, 256, 512):
        h = histogram[start : start + 256]
        cut = int(sum(h) * cutoff_frac)
        acc, lo = 0, 0
        for lo in range(256):
            acc += h[lo]
            if acc > cut:
                break
        acc, hi = 0, 255
        for hi in range(255, -1, -1):
            acc += h[hi]
            if acc > cut:
                break
        widest = max(widest, hi - lo)
    return widest


def prep_subject(cutout_path, bg, target_h, flip=False):
    """Scale, enhance, grade toward the background, rim-light, feather.

    All deterministic Pillow ops on an in-memory copy — the source cutout file
    is never modified and the face is never AI-touched (ADR-0001). Flip happens
    only when the placement decision asks for it.
    """
    with Image.open(cutout_path) as src:
        cut = src.convert("RGBA")
    if flip:
        cut = cut.transpose(Image.FLIP_LEFT_RIGHT)
    scale = target_h / cut.height
    cut = cut.resize((int(cut.width * scale), target_h), Image.LANCZOS)

    mean, rim_color = bg_palette(bg)
    alpha = cut.getchannel("A")
    rgb = cut.convert("RGB")

    # source enhancement: gentle contrast recovery + sharpen (phone photos are
    # soft). Masked to the subject — resize premultiplies the transparent
    # region's RGB to black, which would skew the stretch — and skipped when
    # the subject has no real range to recover: stretching a near-flat
    # histogram blows resize edge-ringing up into a full-range wash.
    opaque = alpha.point(lambda v: 255 if v > 128 else 0)
    if _trimmed_span(rgb.histogram(opaque)) >= 64:
        rgb = ImageOps.autocontrast(rgb, cutoff=1, mask=opaque)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=3))

    # color-grade toward the background palette: subtle 15% tint + luminance match
    tint = Image.new("RGB", rgb.size, mean)
    rgb = Image.blend(rgb, tint, 0.15)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
    if sum(mean) / 3 < 80:  # dark scene: pull brightness down so the subject sits in it
        rgb = ImageEnhance.Brightness(rgb).enhance(0.90)
    rgb = ImageEnhance.Color(rgb).enhance(1.05)

    graded = rgb.convert("RGBA")
    # feathered edge instead of a white sticker outline
    soft_a = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    graded.putalpha(soft_a)

    # thin rim light clamped inside the silhouette — reads as light, not outline
    shifted = ImageChops.offset(soft_a, 7, 3)              # small offset
    edge = ImageChops.subtract(soft_a, shifted)
    edge = edge.filter(ImageFilter.GaussianBlur(1.5))      # tight blur — wide blur = halo
    edge = ImageChops.multiply(edge, soft_a)               # clamp: never spills outside
    edge = edge.point(lambda v: int(v * 0.65))             # subtle, not neon
    rim = Image.new("RGBA", graded.size, rim_color + (0,))
    rim.putalpha(edge)
    graded.alpha_composite(rim)
    return graded


def drop_shadow(canvas, subject, pos):
    shadow_a = subject.getchannel("A").filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", subject.size, (0, 0, 0, 0))
    shadow.putalpha(shadow_a.point(lambda v: int(v * 0.45)))
    canvas.alpha_composite(shadow, (pos[0] - 18, pos[1] + 10))


def compose(background, cutout_path, wording, spec, placement):
    """Background + Subject + Text into the final 1280x720 Candidate.

    Returns (image, layout_boxes). The Subject layer is optional (ADR-0005).
    """
    bg = background.convert("RGB").resize(CANVAS, Image.LANCZOS)
    canvas = bg.convert("RGBA")

    subject_box = None
    text_right = CANVAS[0] - SAFE_MARGIN
    if cutout_path is not None:
        subject = prep_subject(
            cutout_path, bg, int(CANVAS[1] * placement["scale"]), placement["flip"]
        )
        if placement["side"] == "right":
            x = CANVAS[0] - subject.width + EDGE_BLEED
        else:
            x = -EDGE_BLEED
        pos = (x, CANVAS[1] - subject.height)
        drop_shadow(canvas, subject, pos)
        canvas.alpha_composite(subject, pos)
        subject_box = [pos[0], pos[1], subject.width, subject.height]
        if placement["side"] == "right":
            text_right = min(x - 10, text_right)

    zone = (SAFE_MARGIN, SAFE_MARGIN, text_right, CANVAS[1] - SAFE_MARGIN)
    text_box = draw_styled_text(canvas, wording, zone, spec["text_device"], spec["accent"])

    return canvas.convert("RGB"), {"text": text_box, "subject": subject_box}


def split_balanced(words):
    """2-line split minimizing the wider line (by character count)."""
    if len(words) <= 2:
        return [" ".join(words)]
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        width = max(len(a), len(b))
        if best is None or width < best[0]:
            best = (width, [a, b])
    return best[1]


def _fit_font(lines, max_w, max_h, start=170):
    """Largest font whose widest line fits max_w and whose stacked chips fit max_h."""
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    size = start
    while size > 24:
        font = _font(size)
        widths = [probe.textbbox((0, 0), line, font=font)[2] for line in lines]
        chip_h = max(
            probe.textbbox((0, 0), line, font=font)[3] for line in lines
        ) + 2 * CHIP_PAD[1]
        total_h = chip_h * len(lines) + LINE_GAP * (len(lines) - 1)
        if max(widths) <= max_w and total_h <= max_h:
            return font
        size -= 4
    return _font(size)


def _line_chip(line, font, bar_rgb, fg, accent_rgb, accent_last=False, rot=0.0):
    """One line rendered on a filled rounded bar (or bare), optionally rotated."""
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = probe.textbbox((0, 0), line, font=font)
    pw, ph = CHIP_PAD
    chip = Image.new(
        "RGBA", (bbox[2] - bbox[0] + 2 * pw, bbox[3] - bbox[1] + 2 * ph), (0, 0, 0, 0)
    )
    draw = ImageDraw.Draw(chip)
    if bar_rgb is not None:
        draw.rounded_rectangle([0, 0, chip.width - 1, chip.height - 1], 10, fill=bar_rgb)
    words = line.split()
    x = pw
    for i, word in enumerate(words):
        color = accent_rgb if (accent_last and i == len(words) - 1) else fg
        kwargs = {} if bar_rgb is not None else {"stroke_width": 3, "stroke_fill": "black"}
        draw.text((x, ph - bbox[1]), word, font=font, fill=color, **kwargs)
        x += probe.textbbox((0, 0), word + " ", font=font)[2]
    if rot:
        return chip.rotate(rot, expand=True, resample=Image.BICUBIC)
    return chip


def draw_styled_text(canvas, wording, zone, device, accent_hex):
    """Render the Wording into `zone` with the spec's text device.

    Returns the union box [x, y, w, h] actually covered by the rendered text —
    the observable layout box that must sit inside the safe margins.
    """
    x0, y0, x1, y1 = zone
    accent_rgb = hex_rgb(accent_hex)
    lines = split_balanced(wording.upper().split())
    font = _fit_font(lines, x1 - x0 - FIT_PAD, y1 - y0)

    if device == "chips":  # torn-paper white chips, ink text, accent last word
        specs = [(CHIP_PAPER, INK) for _ in lines]
    elif device == "label-bars":  # black bar + accent bar, alternating
        specs = [(BAR_BLACK, WHITE), (accent_rgb, BAR_BLACK)]
    else:  # plain-accent: bare stroked text, accent last word
        specs = [(None, WHITE) for _ in lines]

    chips = []
    for i, line in enumerate(lines):
        bar, fg = specs[i % len(specs)]
        accent_last = (i == len(lines) - 1) and device in ("chips", "plain-accent")
        rot = (1.6 if i % 2 == 0 else -1.4) if device == "chips" else 0.0
        chips.append(_line_chip(line, font, bar, fg, accent_rgb, accent_last, rot))

    total_h = sum(c.height for c in chips) + LINE_GAP * (len(chips) - 1)
    y = int(y0 + (y1 - y0 - total_h) / 2)
    union = None
    for chip in chips:
        x = int(x0 + (x1 - x0 - chip.width) / 2)
        canvas.alpha_composite(chip, (x, y))
        box = (x, y, x + chip.width, y + chip.height)
        union = box if union is None else (
            min(union[0], box[0]),
            min(union[1], box[1]),
            max(union[2], box[2]),
            max(union[3], box[3]),
        )
        y += chip.height + LINE_GAP
    return [union[0], union[1], union[2] - union[0], union[3] - union[1]]
