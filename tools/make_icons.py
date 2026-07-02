#!/usr/bin/env python3
"""Generate UserStamp extension icons to match the AI Contextualizers family.

Family reference (measured from the set):
  - Rounded square filling the canvas, corner radius 12.5% of width, fill #1F2024,
    on a transparent background.
  - The product letter (this repo's initial) as a heavy bold sans capital in
    #FFFFFF, letter ink height ~51% of icon height, optically centered.
  - A square-cut bracket pair in #F02F40 flanking the letter: vertical stems with
    short horizontal arms turned inward at top and bottom. Bracket height ~38% of
    icon height (top ~30.5%, bottom ~68.8%), stroke ~5% of width, arms reaching
    inward ~5% again; left outer edge ~16.4% from the left, right mirrored.
  - At 16px only, the brackets are omitted: just the white letter on the square.

Each size is rendered on a high-resolution buffer and downsampled with LANCZOS
for antialiasing, then written natively at 16/32/48/128 px.

Run from the repo root:  python3 tools/make_icons.py
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

# --- Palette ---------------------------------------------------------------
BG = (0x1F, 0x20, 0x24, 255)      # graphite square
LETTER = (0xFF, 0xFF, 0xFF, 255)  # white letter
BRACKET = (0xF0, 0x2F, 0x40, 255)  # crimson brackets

# --- Geometry (fractions of the icon size) ---------------------------------
CORNER_R = 0.125
LETTER_H = 0.51
STROKE = 0.05
ARM = 0.05
Y_TOP = 0.305
Y_BOT = 0.688
X_OUTER = 0.164   # left bracket outer edge; right is mirrored

SIZES = [16, 32, 48, 128]
NO_BRACKET_AT = 16  # reference behavior: omit brackets at 16px

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(REPO_ROOT, "icons")

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]


def detect_letter():
    """Determine the product letter from the manifest name."""
    try:
        with open(os.path.join(REPO_ROOT, "manifest.json"), encoding="utf-8") as f:
            name = (json.load(f).get("name") or "").strip()
    except (OSError, ValueError):
        name = ""
    lname = name.lower()
    if "geostamp" in lname:
        return "G"
    if "userstamp" in lname:
        return "U"
    if "timestamp" in lname:
        return "T"
    # Fall back to the first capital of the name, else "U" for this repo.
    return (name[:1].upper() or "U")


def load_font_path():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    raise SystemExit("No bold sans font found; install one of: %s" % ", ".join(FONT_CANDIDATES))


def fit_font(font_path, letter, target_h):
    """Return a font whose ink height for `letter` is ~target_h pixels."""
    size = max(1, int(target_h * 1.3))
    for _ in range(6):
        font = ImageFont.truetype(font_path, size)
        l, t, r, b = font.getbbox(letter)
        h = b - t
        if h == 0:
            break
        if abs(h - target_h) <= 1:
            return font
        size = max(1, round(size * target_h / h))
    return ImageFont.truetype(font_path, size)


def draw_bracket(draw, x_outer, y_top, y_bot, t, arm, mirror):
    """Draw one square-cut bracket. mirror=False -> '[', True -> ']'."""
    if not mirror:
        x0 = x_outer
        draw.rectangle([x0, y_top, x0 + t, y_bot], fill=BRACKET)              # stem
        draw.rectangle([x0, y_top, x0 + t + arm, y_top + t], fill=BRACKET)    # top arm
        draw.rectangle([x0, y_bot - t, x0 + t + arm, y_bot], fill=BRACKET)    # bottom arm
    else:
        x1 = x_outer
        draw.rectangle([x1 - t, y_top, x1, y_bot], fill=BRACKET)              # stem
        draw.rectangle([x1 - t - arm, y_top, x1, y_top + t], fill=BRACKET)    # top arm
        draw.rectangle([x1 - t - arm, y_bot - t, x1, y_bot], fill=BRACKET)    # bottom arm


def render(size, letter, font_path):
    ss = max(4, -(-512 // size))  # supersample factor, working buffer >= 512px
    S = size * ss

    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded graphite square filling the canvas.
    draw.rounded_rectangle([0, 0, S - 1, S - 1], radius=CORNER_R * S, fill=BG)

    # Brackets (omitted at 16px per the reference).
    if size != NO_BRACKET_AT:
        t = STROKE * S
        arm = ARM * S
        y_top = Y_TOP * S
        y_bot = Y_BOT * S
        draw_bracket(draw, X_OUTER * S, y_top, y_bot, t, arm, mirror=False)
        draw_bracket(draw, (1 - X_OUTER) * S, y_top, y_bot, t, arm, mirror=True)

    # Letter, optically centered on the canvas by its ink box.
    font = fit_font(font_path, letter, LETTER_H * S)
    l, top, r, b = font.getbbox(letter)
    x = (S - (r - l)) / 2 - l
    y = (S - (b - top)) / 2 - top
    draw.text((x, y), letter, font=font, fill=LETTER)

    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(ICONS_DIR, exist_ok=True)
    letter = detect_letter()
    font_path = load_font_path()
    print("Product letter: %s   font: %s" % (letter, os.path.basename(font_path)))
    for size in SIZES:
        img = render(size, letter, font_path)
        out = os.path.join(ICONS_DIR, "icon%d.png" % size)
        img.save(out, "PNG")
        print("wrote %s (%dx%d)" % (out, img.width, img.height))


if __name__ == "__main__":
    main()
