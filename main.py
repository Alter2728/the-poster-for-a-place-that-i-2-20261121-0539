#!/usr/bin/env python3
"""THRELUNE — a travel poster for a place that does not exist.

Draws a flat, vintage travel-poster style scene with PIL: a floating-island
archipelago at dawn, one great lantern tower as the landmark, a waterfall
pouring off the main island into a sea of cloud, and the invented place's
name set across the sky. Writes one PNG to /output/entry.png.
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

# --- palette -------------------------------------------------------------
INK = (24, 27, 64)          # deep indigo, darkest silhouette
SKY_TOP = (27, 33, 82)
SKY_MID = (58, 74, 140)
SKY_LOW = (120, 116, 176)
SKY_GLOW = (242, 166, 90)   # amber
SKY_PALE = (250, 214, 150)
CREAM = (252, 240, 214)
SUN = (255, 236, 190)
FAR = (138, 142, 196)       # far islands
MID = (82, 88, 158)         # mid islands
NEAR = (44, 48, 104)        # main island rock
NEAR_TOP = (64, 70, 130)
RIM = (246, 178, 106)       # warm rim light on island tops
WATER = (196, 226, 240)
CLOUD = (250, 232, 204)
CLOUD_SHADE = (238, 200, 168)
CORAL = (232, 106, 90)
LAMP = (255, 196, 96)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    for base in (FONT_DIR, Path("/usr/share/fonts/truetype"),
                 Path("/usr/share/fonts")):
        p = base / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size=size)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def sky(d):
    stops = [(0.0, SKY_TOP), (0.34, SKY_MID), (0.55, SKY_LOW),
             (0.72, SKY_GLOW), (0.84, SKY_PALE), (1.0, SKY_PALE)]
    for y in range(H):
        t = y / (H - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                col = lerp(c0, c1, (t - t0) / (t1 - t0))
                break
        d.line([(0, y), (W, y)], fill=col)


def sun(img, cx, cy, r):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    for rr, alpha in ((r * 2.1, 26), (r * 1.7, 40), (r * 1.35, 58)):
        g.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=SUN + (alpha,))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN)


def island(d, cx, top_y, half_w, depth, rock, top_col, rim=True):
    """A flat-topped floating island: plateau + tapered rocky underside."""
    # underside: a few stacked tapering bands for a poster-faceted look
    bands = 5
    for i in range(bands):
        t0, t1 = i / bands, (i + 1) / bands
        y0 = top_y + depth * t0
        y1 = top_y + depth * t1
        w0 = half_w * (1 - 0.82 * t0)
        w1 = half_w * (1 - 0.82 * t1)
        shade = lerp(rock, INK, 0.12 * i)
        d.polygon([(cx - w0, y0), (cx + w0, y0), (cx + w1, y1), (cx - w1, y1)],
                  fill=shade)
    # pointed tip
    d.polygon([(cx - half_w * 0.18, top_y + depth),
               (cx + half_w * 0.18, top_y + depth),
               (cx, top_y + depth + half_w * 0.22)], fill=INK)
    # plateau
    d.rectangle([cx - half_w, top_y - 10, cx + half_w, top_y + 4], fill=top_col)
    if rim:
        d.rectangle([cx - half_w, top_y - 13, cx + half_w, top_y - 9], fill=RIM)


def tree(d, x, y, s, col):
    d.rectangle([x - 2 * s, y - 14 * s, x + 2 * s, y], fill=col)
    d.ellipse([x - 11 * s, y - 34 * s, x + 11 * s, y - 10 * s], fill=col)
    d.ellipse([x - 7 * s, y - 42 * s, x + 7 * s, y - 24 * s], fill=col)


def house(d, x, y, s, body, roof):
    d.rectangle([x - 16 * s, y - 20 * s, x + 16 * s, y], fill=body)
    d.polygon([(x - 20 * s, y - 20 * s), (x + 20 * s, y - 20 * s),
               (x, y - 36 * s)], fill=roof)
    d.rectangle([x - 4 * s, y - 13 * s, x + 4 * s, y - 5 * s], fill=LAMP)


def tower(d, cx, base_y):
    """The landmark: a tall banded lantern tower with a glowing lamp room."""
    top_y = base_y - 300
    # tapered shaft, banded
    bands = 6
    for i in range(bands):
        t0, t1 = i / bands, (i + 1) / bands
        y0 = base_y - 300 * t0
        y1 = base_y - 300 * t1
        w0 = 46 - 20 * t0
        w1 = 46 - 20 * t1
        col = NEAR if i % 2 == 0 else lerp(NEAR, CREAM, 0.22)
        d.polygon([(cx - w0, y0), (cx + w0, y0), (cx + w1, y1), (cx - w1, y1)],
                  fill=col)
    # gallery + lamp room
    d.rectangle([cx - 34, top_y - 8, cx + 34, top_y + 2], fill=INK)
    d.rectangle([cx - 22, top_y - 52, cx + 22, top_y - 8], fill=LAMP)
    d.rectangle([cx - 22, top_y - 52, cx - 18, top_y - 8], fill=INK)
    d.rectangle([cx + 18, top_y - 52, cx + 22, top_y - 8], fill=INK)
    d.rectangle([cx - 2, top_y - 52, cx + 2, top_y - 8], fill=INK)
    # dome cap
    d.pieslice([cx - 30, top_y - 92, cx + 30, top_y - 32], 180, 360, fill=CORAL)
    d.rectangle([cx - 30, top_y - 62, cx + 30, top_y - 52], fill=CORAL)
    d.ellipse([cx - 5, top_y - 100, cx + 5, top_y - 90], fill=CORAL)
    # a few lit windows down the shaft
    for wy in (base_y - 70, base_y - 150, base_y - 230):
        d.rectangle([cx - 5, wy - 8, cx + 5, wy + 8], fill=LAMP)


def waterfall(img, x, y0, y1):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, (dx, wdt, alpha) in enumerate(
            [(-16, 10, 150), (-4, 14, 190), (9, 9, 150), (20, 6, 110)]):
        d.line([(x + dx, y0), (x + dx, y1)], fill=WATER + (alpha,), width=wdt)
    for yy in range(y1 - 60, y1, 14):  # mist puffs at the foot
        r = 16 + (yy % 3) * 5
        d.ellipse([x - r, yy - r // 2, x + r, yy + r // 2], fill=WATER + (90,))
    img.alpha_composite(layer)


def clouds(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rows = [(880, CLOUD_SHADE, 255), (930, CLOUD, 255), (980, CREAM, 255)]
    puffs = [(70, 60), (210, 84), (360, 58), (500, 92), (650, 64),
             (790, 88), (920, 62), (1010, 80)]
    for base_y, col, alpha in rows:
        for cx, r in puffs:
            d.ellipse([cx - r, base_y - r // 2, cx + r, base_y + r // 2],
                      fill=col + (alpha,))
        d.rectangle([0, base_y, W, H], fill=col + (alpha,))
    img.alpha_composite(layer)


def beam(img, cx, cy):
    """A soft lantern beam sweeping out over the cloud sea."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon([(cx - 14, cy), (cx - 330, cy + 210), (cx - 300, cy + 270),
               (cx - 10, cy + 22)], fill=LAMP + (46,))
    d.polygon([(cx + 14, cy), (cx + 300, cy + 190), (cx + 272, cy + 248),
               (cx + 10, cy + 22)], fill=LAMP + (34,))
    img.alpha_composite(layer)


def stars(d, pts):
    for x, y, r in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=CREAM)


def birds(d, pts, col, s=1.0):
    for x, y in pts:
        d.arc([x - 16 * s, y - 8 * s, x, y + 8 * s], 200, 340, fill=col,
              width=max(2, int(3 * s)))
        d.arc([x, y - 8 * s, x + 16 * s, y + 8 * s], 200, 340, fill=col,
              width=max(2, int(3 * s)))


def spaced_text(d, cx, y, s, fnt, fill, tracking):
    widths = [d.textlength(ch, font=fnt) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, wdt in zip(s, widths):
        d.text((x, y), ch, font=fnt, fill=fill, anchor="la")
        x += wdt + tracking
    return total


def main():
    img = Image.new("RGBA", (W, H), SKY_TOP + (255,))
    d = ImageDraw.Draw(img)

    sky(d)
    stars(d, [(96, 36, 2), (210, 24, 2), (330, 44, 2), (452, 28, 2),
              (560, 40, 2), (672, 26, 2), (788, 42, 2), (902, 30, 2),
              (150, 250, 2), (880, 240, 2)])
    sun(img, 512, 618, 148)
    d = ImageDraw.Draw(img)

    # far islands
    island(d, 150, 330, 74, 70, FAR, lerp(FAR, CREAM, 0.25), rim=False)
    island(d, 862, 288, 58, 56, FAR, lerp(FAR, CREAM, 0.25), rim=False)
    island(d, 742, 392, 44, 44, FAR, lerp(FAR, CREAM, 0.25), rim=False)

    # mid islands
    island(d, 236, 452, 120, 104, MID, lerp(MID, CREAM, 0.18))
    tree(d, 196, 442, 1.0, MID)
    tree(d, 262, 442, 0.8, MID)
    island(d, 820, 486, 96, 84, MID, lerp(MID, CREAM, 0.18))
    tree(d, 800, 476, 0.9, MID)
    house(d, 848, 476, 0.7, MID, INK)

    # main island with the landmark
    island(d, 470, 648, 300, 210, NEAR, NEAR_TOP)
    tower(d, 372, 640)
    house(d, 500, 638, 1.1, NEAR, CORAL)
    house(d, 566, 638, 0.9, NEAR, CORAL)
    house(d, 618, 638, 0.75, NEAR, CORAL)
    tree(d, 452, 638, 1.2, INK)
    tree(d, 676, 638, 1.0, INK)
    tree(d, 250, 638, 1.1, INK)

    # waterfall off the right edge of the main island
    waterfall(img, 742, 652, 916)
    d = ImageDraw.Draw(img)

    # small foreground islet, lower left
    island(d, 128, 762, 86, 76, INK, lerp(INK, CREAM, 0.14))
    tree(d, 120, 752, 1.0, INK)

    clouds(img)
    beam(img, 372, 310)
    d = ImageDraw.Draw(img)

    birds(d, [(250, 300), (300, 322), (712, 262), (758, 282)], INK, 1.0)
    birds(d, [(322, 252), (668, 238)], lerp(INK, CREAM, 0.3), 0.8)

    # --- typography: the place's name, and nothing else ------------------
    name_font = font("DejaVuSans-Bold.ttf", 118)
    tw = spaced_text(d, 512, 58, "THRELUNE", name_font, CREAM, 26)
    # thin rule with a centre diamond under the name
    ry = 212
    d.line([(512 - tw / 2, ry), (512 - 26, ry)], fill=CREAM, width=3)
    d.line([(512 + 26, ry), (512 + tw / 2, ry)], fill=CREAM, width=3)
    d.polygon([(512, ry - 9), (521, ry), (512, ry + 9), (503, ry)], fill=CORAL)

    out = Path(os.environ.get("OUT", "/output/entry.png"))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
