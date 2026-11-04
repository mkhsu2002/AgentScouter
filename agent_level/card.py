"""Result card generator for the Agent Level Calculator.

Renders a PNG result card: the logo at the top left, name, species,
optional birthday, level badge, five-dimension radar chart, a social
share prompt with hashtags, the "Test version v0.01" note at the
bottom right, and a share line at the bottom left pointing to the
Pages site.

Card size is 1080 x 1920 (9:16, for vertical social posts and
stories). Fonts: tries common CJK font locations and falls back to
PIL's default font (which cannot render CJK) when none is found;
install a CJK font for correct Chinese labels.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

CARD_VERSION_LABEL = "Test version v0.01"
CARD_WIDTH = 1080
CARD_HEIGHT = 1920
CARD_SHARE_PROMPT = "What level is your AI agent?"
CARD_SHARE_TAGS = "#AgentScouter #AIAgents"
CARD_SHARE_URL = "mkhsu2002.github.io/AgentScouter"
NAVY = (11, 42, 74)
VIOLET_HEX = "#7c5cd6"
DARK_VIOLET_HEX = "#4c1d95"

_FONT_REGULAR = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:\\Windows\\Fonts\\msyh.ttc",
]
_FONT_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:\\Windows\\Fonts\\msyhbd.ttc",
]


def _load_font(size, bold=False):
    for path in _FONT_BOLD if bold else _FONT_REGULAR:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=0)
            except Exception:
                continue
    return ImageFont.load_default()


def _text(draw, xy, text, font, fill, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def _radar_point(cx, cy, radius, frac, k):
    angle = math.radians(72 * k)
    return (
        cx + radius * frac * math.sin(angle),
        cy - radius * frac * math.cos(angle),
    )


def draw_radar(img, cx, cy, radius, values, labels, avg,
               f_label, f_val, f_ring):
    """Draw the radar chart onto `img`, returning the new image."""
    draw = ImageDraw.Draw(img)
    for ring in (20, 40, 60, 80, 100):
        pts = [_radar_point(cx, cy, radius, ring / 100, k) for k in range(5)]
        draw.line(pts + [pts[0]], fill="#cccccc", width=2)
        draw.text((cx + 48, cy - radius * ring / 100 - 12), str(ring),
                  font=f_ring, fill="#999999")
    for k in range(5):
        draw.line([(cx, cy), _radar_point(cx, cy, radius, 1.0, k)],
                  fill="#dddddd", width=2)
    avg_pts = [_radar_point(cx, cy, radius, avg / 100, k) for k in range(5)]
    for i in range(5):
        x0, y0 = avg_pts[i]
        x1, y1 = avg_pts[(i + 1) % 5]
        for s in range(0, 12, 2):
            t0, t1 = s / 12, (s + 1) / 12
            draw.line(
                [(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                 (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                fill="#999999", width=2)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    vpts = [_radar_point(cx, cy, radius, v / 100, k)
            for k, v in enumerate(values)]
    overlay_draw.polygon(vpts, fill=(124, 92, 214, 70),
                         outline=(124, 92, 214, 255), width=5)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.line(vpts + [vpts[0]], fill=VIOLET_HEX, width=5)
    for x, y in vpts:
        draw.ellipse([x - 11, y - 11, x + 11, y + 11],
                     fill=VIOLET_HEX, outline="white", width=3)
    for k, label in enumerate(labels):
        lx, ly = _radar_point(cx, cy, radius, 1.18, k)
        _text(draw, (lx, ly), label, f_label, "#222222")
    for k, value in enumerate(values):
        vx, vy = _radar_point(cx, cy, radius, value / 100 - 0.10, k)
        _text(draw, (vx, vy), str(value), f_val, DARK_VIOLET_HEX)
    return img


def generate_card(result, name="Unnamed", species="AI Agent", birthday=None,
                  logo_path=None, output_path="agentscouter-card.png"):
    """Render the result card PNG. Returns the output path."""
    width, height = CARD_WIDTH, CARD_HEIGHT
    cx = width // 2
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    f_title = _load_font(42, bold=True)
    f_name = _load_font(78, bold=True)
    f_info = _load_font(34)
    f_level = _load_font(58, bold=True)
    f_sub = _load_font(30)
    f_label = _load_font(30, bold=True)
    f_val = _load_font(32, bold=True)
    f_ring = _load_font(20)
    f_ver = _load_font(24)
    f_share = _load_font(26)
    f_prompt = _load_font(36, bold=True)
    f_tags = _load_font(28, bold=True)

    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            w, h = logo.size
            new_w = 300
            logo = logo.resize((new_w, round(h * new_w / w)))
            img.paste(logo, (60, 50), logo)
        except Exception:
            pass
    draw = ImageDraw.Draw(img)

    _text(draw, (cx, 310), "AgentScouter Test Result Card", f_title, "#111111")
    _text(draw, (cx, 435), name, f_name, "#111111")
    _text(draw, (cx, 540), f"Species: {species}", f_info, "#333333")
    if birthday:
        _text(draw, (cx, 600), f"Birthday: {birthday}", f_info, "#333333")

    badge_text = f"Lv.{result['level']} {result['title']}"
    bbox = draw.textbbox((0, 0), badge_text, font=f_level)
    text_w = bbox[2] - bbox[0]
    bx0, bx1 = cx - text_w // 2 - 50, cx + text_w // 2 + 50
    by0, by1 = 660, 765
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=30, fill=NAVY)
    _text(draw, (cx, (by0 + by1) // 2), badge_text, f_level, "white")
    _text(draw, (cx, 810),
          f"Composite {result['composite']} | INT {result['intelligence']}",
          f_sub, "#444444")

    dims = result["dimensions"]
    values = [dims[k]["score"] for k in ("HUM", "KNOW", "SKILL", "SPAN", "REL")]
    labels = ["Humanity HUM", "Knowledge KNOW", "Skill SKILL", "Span SPAN", "Reliability REL"]
    img = draw_radar(img, cx, 1240, 300, values, labels,
                     result["composite"], f_label, f_val, f_ring)
    draw = ImageDraw.Draw(img)
    _text(draw, (cx, 1680), CARD_SHARE_PROMPT, f_prompt, "#0B2A4A")
    _text(draw, (cx, 1735), f"Try it: {CARD_SHARE_URL}", f_share, "#444444")
    _text(draw, (cx, 1785), CARD_SHARE_TAGS, f_tags, VIOLET_HEX)
    _text(draw, (width - 60, 1885), CARD_VERSION_LABEL, f_ver, "#666666",
          anchor="rm")
    _text(draw, (60, 1885),
          f"Share your card: {CARD_SHARE_URL}",
          f_share, "#666666", anchor="lm")
    img.save(output_path)
    return output_path
