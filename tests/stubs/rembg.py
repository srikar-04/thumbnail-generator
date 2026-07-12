"""Offline stand-in for rembg (the real one downloads its model on first use).
Same oval matte as FakeCutoutEngine — enough for the cutout consumers."""

from PIL import Image, ImageDraw


def remove(img):
    cutout = img.convert("RGBA")
    mask = Image.new("L", cutout.size, 0)
    width, height = cutout.size
    ImageDraw.Draw(mask).ellipse(
        [width // 8, height // 12, width * 7 // 8, height], fill=255
    )
    cutout.putalpha(mask)
    return cutout
