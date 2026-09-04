#!/usr/bin/env python3
"""Render a white-background animated cheatsheet derived from a LinkedIn architecture exchange."""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "images" / "linkedin-shabina-scope-composition-cheatsheet"
WIDTH, HEIGHT = 1080, 1350
FPS = 15
DURATION = 9

WHITE = "#FFFFFF"
PAPER = "#F5F9FF"
INK = "#081426"
BLUE = "#075BDA"
BRIGHT_BLUE = "#1683FF"
PALE_BLUE = "#DDEBFF"
LINE = "#BCD4F4"
SOFT_LINE = "#E3EEFC"

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")


def fnt(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def mix(a: int, b: int, amount: float) -> int:
    return round(a + (b - a) * amount)


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def blend(a: str, b: str, amount: float) -> tuple[int, int, int]:
    ar, ag, ab = rgb(a)
    br, bg, bb = rgb(b)
    return mix(ar, br, amount), mix(ag, bg, amount), mix(ab, bb, amount)


def txt(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int,
        color: str = INK, bold: bool = False, anchor: str | None = None) -> None:
    draw.text(xy, value, font=fnt(size, bold), fill=color, anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int,
            fill: str | tuple[int, int, int], outline: str = LINE, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int],
          color: str = BLUE, width: int = 4, dashed: bool = False) -> None:
    x1, y1 = start
    x2, y2 = end
    if dashed:
        steps = 12
        for i in range(0, steps, 2):
            p1 = i / steps
            p2 = min(1.0, (i + 1) / steps)
            draw.line((mix(x1, x2, p1), mix(y1, y2, p1), mix(x1, x2, p2), mix(y1, y2, p2)),
                      fill=color, width=width)
    else:
        draw.line((x1, y1, x2, y2), fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    length = 12
    wing = 0.55
    draw.polygon([
        (x2, y2),
        (x2 - length * math.cos(angle - wing), y2 - length * math.sin(angle - wing)),
        (x2 - length * math.cos(angle + wing), y2 - length * math.sin(angle + wing)),
    ], fill=color)


def glow(image: Image.Image, center: tuple[int, int], radius: int, intensity: float) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((center[0] - radius, center[1] - radius,
               center[0] + radius, center[1] + radius),
              fill=(*rgb(BRIGHT_BLUE), round(80 * intensity)))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius / 2)))


def badge(draw: ImageDraw.ImageDraw, x: int, y: int, label: str) -> None:
    width = int(draw.textlength(label, font=fnt(15, True))) + 28
    rounded(draw, (x, y, x + width, y + 32), 16, PAPER, BLUE, 2)
    txt(draw, (x + 14, y + 16), label, 15, BLUE, True, "lm")


def section_title(draw: ImageDraw.ImageDraw, y: int, number: str, title: str, caption: str) -> None:
    txt(draw, (54, y), number, 18, BLUE, True)
    txt(draw, (93, y - 3), title, 22, INK, True)
    txt(draw, (1025, y), caption, 13, BLUE, True, "ra")


def draw_header(draw: ImageDraw.ImageDraw) -> None:
    badge(draw, 54, 38, "DYNAMIC CHEATSHEET · 02")
    badge(draw, 850, 38, "WHITE SYSTEM")
    txt(draw, (54, 94), "SCOPE ATTENUATION ≠", 48, INK, True)
    txt(draw, (54, 146), "COMPOSED-ACTION SAFETY", 48, BLUE, True)
    txt(draw, (54, 210), "A production control model needs one invariant for delegation—and another for business effect.", 19, INK)
    draw.line((54, 253, 1026, 253), fill=BLUE, width=4)


def draw_delegation(image: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    y = 284
    section_title(draw, y, "01", "DELEGATION INVARIANT", "PERMISSION MAY ONLY NARROW")
    rounded(draw, (44, y + 35, 1036, y + 244), 22, WHITE, LINE, 2)
    labels = [("SUBJECT", "S0", 128), ("AGENT", "S1", 103), ("TOOL A", "S2", 78), ("TOOL B", "S3", 55)]
    xs = [112, 314, 516, 718]
    center_y = y + 137
    for i, ((label, scope, width), x) in enumerate(zip(labels, xs)):
        active_float = (t * 0.9) % 4
        active = int(active_float) == i
        if active:
            glow(image, (x, center_y), 42, 0.7 + 0.3 * math.sin(t * 5) ** 2)
        draw.ellipse((x - 31, center_y - 31, x + 31, center_y + 31),
                     fill=PAPER, outline=BRIGHT_BLUE if active else BLUE, width=4)
        txt(draw, (x, center_y), scope, 19, BLUE, True, "mm")
        txt(draw, (x, center_y + 50), label, 13, INK, True, "mm")
        draw.rounded_rectangle((x - width // 2, center_y + 75, x + width // 2, center_y + 88),
                               radius=6, fill=BLUE)
        if i < 3:
            arrow(draw, (x + 42, center_y), (xs[i + 1] - 42, center_y), BLUE, 3)

    formula_x = 834
    rounded(draw, (790, y + 65, 1012, y + 207), 18, PAPER, BLUE, 2)
    txt(draw, (formula_x, y + 91), "CRYPTOGRAPHIC BOUND", 13, BLUE, True)
    txt(draw, (formula_x, y + 130), "S[i+1] <= S[i]", 27, INK, True)
    txt(draw, (formula_x, y + 169), "for every delegation hop", 14, BLUE, True)
    txt(draw, (66, y + 224), "Necessary: blocks ambient scope expansion. Insufficient alone: permitted effects can still compose into a larger consequence.", 15, INK)

    for offset in (0.0, 0.45):
        p = (t * 0.2 + offset) % 1.0
        x = mix(xs[0] + 40, xs[-1] - 40, p)
        glow(image, (x, center_y), 9, 0.9)
        draw.ellipse((x - 5, center_y - 5, x + 5, center_y + 5), fill=BRIGHT_BLUE)


def clock_card(draw: ImageDraw.ImageDraw, image: Image.Image, box: tuple[int, int, int, int],
               index: int, heading: str, line1: str, line2: str, t: float) -> None:
    x1, y1, x2, y2 = box
    active = int((t * 0.75) % 3) == index
    rounded(draw, box, 18, blend(WHITE, PALE_BLUE, 0.55 if active else 0.18),
            BRIGHT_BLUE if active else LINE, 3 if active else 2)
    cx, cy = x1 + 43, y1 + 44
    if active:
        glow(image, (cx, cy), 28, 0.7)
    draw.ellipse((cx - 21, cy - 21, cx + 21, cy + 21), fill=WHITE, outline=BLUE, width=3)
    angle = t * (1.7 + index * 0.45)
    draw.line((cx, cy, cx + 13 * math.cos(angle), cy + 13 * math.sin(angle)), fill=BLUE, width=3)
    draw.line((cx, cy, cx + 8 * math.cos(-angle * 0.55), cy + 8 * math.sin(-angle * 0.55)), fill=INK, width=2)
    txt(draw, (x1 + 76, y1 + 22), heading, 17, INK, True)
    txt(draw, (x1 + 21, y1 + 82), line1, 14, BLUE, True)
    txt(draw, (x1 + 21, y1 + 106), line2, 14, INK)


def draw_clocks(image: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    y = 558
    section_title(draw, y, "02", "THREE-CLOCK GOVERNANCE", "DRIFT CHANGES ADMISSIBILITY")
    rounded(draw, (44, y + 35, 1036, y + 229), 22, WHITE, LINE, 2)
    cards = [
        ("EVENT-TIME", "structure changed", "suspend immediately"),
        ("ATTESTATION-TIME", "conditions changed", "re-validate authority"),
        ("EXECUTION-TIME", "action evaluated", "recheck admissibility"),
    ]
    for i, card in enumerate(cards):
        x = 66 + i * 315
        clock_card(draw, image, (x, y + 62, x + 292, y + 192), i, *card, t)
    txt(draw, (66, y + 214), "Cadence model:", 14, BLUE, True)
    txt(draw, (185, y + 214), "T_att(n,sigma) = T0 / [1 + a(n-1) + b*sigma]", 18, INK, True)
    txt(draw, (770, y + 214), "longer chain → shorter interval", 14, BLUE, True)


def effect_node(draw: ImageDraw.ImageDraw, image: Image.Image, x: int, y: int,
                title: str, body: str, active: bool) -> None:
    rounded(draw, (x - 92, y - 39, x + 92, y + 39), 16,
            blend(WHITE, PALE_BLUE, 0.6 if active else 0.18), BRIGHT_BLUE if active else LINE,
            3 if active else 2)
    if active:
        glow(image, (x, y), 35, 0.55)
    txt(draw, (x, y - 11), title, 14, BLUE, True, "mm")
    txt(draw, (x, y + 14), body, 12, INK, False, "mm")


def draw_composition(image: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    y = 825
    section_title(draw, y, "03", "COMPOSED-TRANSACTION GATE", "PLANNING-TIME CONSEQUENCE CHECK")
    rounded(draw, (44, y + 35, 1036, y + 258), 22, WHITE, LINE, 2)
    action_y = [y + 88, y + 145, y + 202]
    action_labels = [("E1", "CRM delta"), ("E2", "priority shift"), ("E3", "customer promise")]
    active_float = (t * 0.9) % 5
    for i, ((title, body), ay) in enumerate(zip(action_labels, action_y)):
        effect_node(draw, image, 150, ay, title, body, int(active_float) == i)
        arrow(draw, (246, ay), (355, y + 145), BLUE, 3)

    effect_node(draw, image, 455, y + 145, "E1 + E2 + E3", "effect graph", int(active_float) == 3)
    arrow(draw, (551, y + 145), (624, y + 145), BLUE, 4)
    effect_node(draw, image, 721, y + 145, "R_c <= B?", "consequence budget", int(active_float) == 4)
    arrow(draw, (817, y + 145), (869, y + 145), BLUE, 4)
    rounded(draw, (880, y + 97, 1012, y + 193), 18, PALE_BLUE, BLUE, 3)
    txt(draw, (946, y + 126), "ISSUE", 13, BLUE, True, "mm")
    txt(draw, (946, y + 153), "ACTION LEASE", 15, INK, True, "mm")
    txt(draw, (946, y + 176), "+ verifier", 12, BLUE, True, "mm")

    txt(draw, (302, y + 233), "R_c = 1 - PROD(1-r_i) + k_x X + k_i I + k_d D", 16, INK, True, "mm")
    txt(draw, (760, y + 233), "ALLOW = narrow scope + R_c<=B + postconditions + admissible recovery",
        13, BLUE, True, "mm")

    # Converging evidence packets animate the semantic-composition check.
    for idx, ay in enumerate(action_y):
        p = (t * 0.33 + idx * 0.22) % 1.0
        x = mix(248, 352, p)
        yy = mix(ay, y + 145, p)
        draw.ellipse((x - 4, yy - 4, x + 4, yy + 4), fill=BRIGHT_BLUE)


def draw_scorecard(draw: ImageDraw.ImageDraw, t: float) -> None:
    y = 1120
    rounded(draw, (44, y, 1036, y + 169), 22, PAPER, LINE, 2)
    txt(draw, (66, y + 25), "04", 18, BLUE, True)
    txt(draw, (104, y + 22), "CONTROL SCORECARD", 21, INK, True)
    txt(draw, (1012, y + 25), "EXAMPLE OPERATING MEASURES · NOT OBSERVED AUTHHUB RESULTS", 11, BLUE, True, "ra")
    measures = [
        ("SCOPE EXPANSIONS", "blocked / 10k", 0.93),
        ("STALE ATTESTATION", "breaches / 10k", 0.22),
        ("COMPOSITE FN RATE", "missed effects", 0.16),
        ("P95 REVOCATION", "seconds", 0.62),
        ("POSTCONDITION", "violations / 10k", 0.28),
        ("RECOVERY", "verified success", 0.88),
    ]
    reveal = ease((t - 1.2) / 2.2)
    for i, (title, sub, value) in enumerate(measures):
        x = 66 + i * 160
        txt(draw, (x, y + 69), title, 10, BLUE, True)
        txt(draw, (x, y + 91), sub, 11, INK)
        draw.rounded_rectangle((x, y + 121, x + 130, y + 133), radius=6, fill=SOFT_LINE)
        draw.rounded_rectangle((x, y + 121, x + round(130 * value * reveal), y + 133), radius=6, fill=BLUE)
    txt(draw, (54, 1325), "CONTEXT: PUBLIC LINKEDIN EXCHANGE WITH SHABINA ABBA NOORMOHAMED · 04 SEP 2026",
        12, BLUE, True)


def render_frame(frame: int) -> Image.Image:
    t = frame / FPS
    image = Image.new("RGBA", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)

    for x in range(0, WIDTH, 54):
        draw.line((x, 0, x, HEIGHT), fill="#F1F6FD", width=1)
    for y in range(0, HEIGHT, 54):
        draw.line((0, y, WIDTH, y), fill="#F1F6FD", width=1)

    draw_header(draw)
    draw_delegation(image, draw, t)
    draw_clocks(image, draw, t)
    draw_composition(image, draw, t)
    draw_scorecard(draw, t)

    progress = (t % DURATION) / DURATION
    draw.rectangle((0, HEIGHT - 7, WIDTH, HEIGHT), fill=PALE_BLUE)
    draw.rectangle((0, HEIGHT - 7, round(WIDTH * progress), HEIGHT), fill=BLUE)
    return image.convert("RGB")


def encode() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = FPS * DURATION
    with tempfile.TemporaryDirectory(prefix="scope-composition-") as temporary:
        frame_dir = Path(temporary)
        for index in range(total):
            render_frame(index).save(frame_dir / f"frame-{index:04d}.png", optimize=True)

        render_frame(round(FPS * 4.3)).save(
            OUTPUT_DIR / "scope-attenuation-composed-action-safety-poster.png", optimize=True
        )
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
            "-i", str(frame_dir / "frame-%04d.png"), "-c:v", "libx264", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(OUTPUT_DIR / "scope-attenuation-composed-action-safety.mp4"),
        ], check=True)
        palette = frame_dir / "palette.png"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
            "-i", str(frame_dir / "frame-%04d.png"), "-vf",
            "fps=12,scale=720:-1:flags=lanczos,palettegen=max_colors=128", str(palette),
        ], check=True)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
            "-i", str(frame_dir / "frame-%04d.png"), "-i", str(palette), "-lavfi",
            "fps=12,scale=720:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
            "-loop", "0", str(OUTPUT_DIR / "scope-attenuation-composed-action-safety.gif"),
        ], check=True)
    print(f"rendered Shabina-context cheatsheet in {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    encode()
