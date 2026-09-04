#!/usr/bin/env python3
"""Render an original animated LinkedIn cheatsheet for production AI agents."""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "images" / "linkedin-dynamic-cheatsheet-sample"
WIDTH, HEIGHT = 1080, 1350
FPS = 15
DURATION_SECONDS = 8

BG = "#07111F"
PANEL = "#0D1A2B"
PANEL_2 = "#112238"
GRID = "#17304A"
WHITE = "#F5F8FC"
MUTED = "#A8B8C8"
CYAN = "#37CFFF"
BLUE = "#6B8CFF"
TEAL = "#35E6A5"
GOLD = "#FFC857"
RED = "#FF6B75"

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def mix(a: int, b: int, amount: float) -> int:
    return round(a + (b - a) * amount)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def mix_color(a: str, b: str, amount: float) -> tuple[int, int, int]:
    ar, ag, ab = hex_rgb(a)
    br, bg, bb = hex_rgb(b)
    return mix(ar, br, amount), mix(ag, bg, amount), mix(ab, bb, amount)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int,
            fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int,
         color: str = WHITE, bold: bool = False, anchor: str | None = None) -> None:
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int], label: str, color: str) -> None:
    x, y = xy
    f = font(16, True)
    width = int(draw.textlength(label, font=f)) + 30
    rounded(draw, (x, y, x + width, y + 34), 17, mix_color(BG, color, 0.18), color, 2)
    draw.text((x + 15, y + 17), label, font=f, fill=color, anchor="lm")


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int],
          color: str, width: int = 4) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    length = 13
    wing = 0.55
    points = [
        (x2, y2),
        (x2 - length * math.cos(angle - wing), y2 - length * math.sin(angle - wing)),
        (x2 - length * math.cos(angle + wing), y2 - length * math.sin(angle + wing)),
    ]
    draw.polygon(points, fill=color)


def glow_circle(image: Image.Image, center: tuple[int, int], radius: int, color: str,
                intensity: float) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hex_rgb(color)
    d.ellipse((center[0] - radius, center[1] - radius,
               center[0] + radius, center[1] + radius), fill=(*rgb, round(130 * intensity)))
    layer = layer.filter(ImageFilter.GaussianBlur(radius / 2))
    image.alpha_composite(layer)


def draw_header(draw: ImageDraw.ImageDraw, intro: float) -> None:
    pill(draw, (54, 45), "DYNAMIC CHEATSHEET · 01", CYAN)
    pill(draw, (808, 45), "LIVE FLOW", TEAL)
    title_color = mix_color(BG, WHITE, intro)
    text(draw, (54, 105), "PRODUCTION AI AGENTS", 56, title_color, True)
    text(draw, (54, 170), "THE CONTROLLED-EXECUTION CHEATSHEET", 30, CYAN, True)
    text(draw, (54, 218), "Average accuracy does not bound tail risk. Every material action needs three proofs.", 20, MUTED)


def draw_top_flow(image: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    labels = ["INTENT", "EVIDENCE", "PLAN", "RISK", "LEASE", "ACTION", "VERIFY"]
    colors = [BLUE, BLUE, BLUE, GOLD, GOLD, TEAL, TEAL]
    xs = [82, 235, 388, 541, 694, 847, 1000]
    y = 318
    for i in range(len(xs) - 1):
        arrow(draw, (xs[i] + 43, y), (xs[i + 1] - 43, y), GRID, 4)

    active = int((t * 1.15) % len(labels))
    for i, (x, label, color) in enumerate(zip(xs, labels, colors)):
        phase = max(0.0, 1.0 - abs(i - ((t * 1.15) % len(labels))))
        pulse = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 5.5)) if i == active else phase * 0.35
        if pulse > 0.05:
            glow_circle(image, (x, y), 36, color, pulse)
        draw.ellipse((x - 28, y - 28, x + 28, y + 28), fill=PANEL_2, outline=color, width=4)
        text(draw, (x, y), str(i + 1), 20, color, True, "mm")
        text(draw, (x, y + 48), label, 14, WHITE if i == active else MUTED, True, "mm")

    # Three moving packets make the static flow feel operational.
    for offset in (0.0, 0.34, 0.68):
        p = (t * 0.18 + offset) % 1.0
        x = mix(xs[0] + 40, xs[-1] - 40, p)
        glow_circle(image, (x, y), 10, CYAN, 0.8)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=WHITE)


def small_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], index: str,
               heading: str, body: str, color: str, active: bool) -> None:
    fill = mix_color(PANEL, color, 0.12 if active else 0.04)
    rounded(draw, box, 18, fill, color if active else GRID, 3 if active else 2)
    x1, y1, x2, _ = box
    draw.ellipse((x1 + 18, y1 + 18, x1 + 50, y1 + 50), fill=color)
    text(draw, (x1 + 34, y1 + 34), index, 15, BG, True, "mm")
    text(draw, (x1 + 62, y1 + 20), heading, 18, WHITE, True)
    lines = body.split("\n")
    for line_no, line in enumerate(lines):
        text(draw, (x1 + 20, y1 + 67 + 24 * line_no), line, 15, MUTED)
    if active:
        draw.rectangle((x1 + 20, y1 + 129, x2 - 20, y1 + 134), fill=color)


def section(draw: ImageDraw.ImageDraw, y: int, number: str, title_value: str,
            kicker: str, color: str, cards: list[tuple[str, str]], active_index: int,
            reveal: float) -> None:
    height = 212
    border = mix_color(GRID, color, 0.65 * reveal)
    rounded(draw, (44, y, 1036, y + height), 24, PANEL, border, 3)
    text(draw, (66, y + 31), number, 20, color, True)
    text(draw, (106, y + 28), title_value, 23, WHITE, True)
    text(draw, (1010, y + 31), kicker, 14, color, True, "rm")
    card_y = y + 72
    card_w = 296
    for i, (heading, body) in enumerate(cards):
        x = 66 + i * 318
        small_card(draw, (x, card_y, x + card_w, card_y + 120), str(i + 1), heading, body,
                   color, i == active_index)


def draw_recovery_loop(image: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    y = 1023
    # The recovery branch becomes visible midway through the loop.
    branch = ease((math.sin(t * 0.9 - 1.2) + 1) / 2)
    color = mix_color(GRID, RED, branch)
    draw.line((876, y - 35, 876, y + 27, 566, y + 27), fill=color, width=4)
    arrow(draw, (566, y + 27), (566, y - 18), color, 4)
    rounded(draw, (614, y + 8, 828, y + 47), 18, mix_color(PANEL, RED, 0.14 * branch), color, 2)
    text(draw, (721, y + 28), "STOP · RECONCILE · RECOVER", 13, color, True, "mm")
    if branch > 0.25:
        p = (t * 0.55) % 1.0
        x = mix(856, 588, p)
        glow_circle(image, (x, y + 27), 8, RED, branch)
        draw.ellipse((x - 4, y + 23, x + 4, y + 31), fill=RED)


def draw_metrics(draw: ImageDraw.ImageDraw, t: float) -> None:
    y = 1122
    rounded(draw, (44, y, 1036, 1297), 24, PANEL, GRID, 2)
    text(draw, (66, y + 27), "05", 20, CYAN, True)
    text(draw, (106, y + 24), "OPERATING SCORECARD", 23, WHITE, True)
    text(draw, (1010, y + 27), "ILLUSTRATIVE TARGETS · NOT BENCHMARK DATA", 12, MUTED, True, "rm")
    metrics = [
        ("HARMFUL ACTIONS", "<0.1%", RED, 0.23),
        ("POSTCONDITION COVERAGE", "≥99.9%", TEAL, 0.93),
        ("P95 REVOCATION", "<30s", GOLD, 0.70),
        ("DUPLICATE EFFECTS", "0", BLUE, 0.06),
        ("RECOVERY SUCCESS", "≥95%", CYAN, 0.88),
    ]
    reveal = ease((t - 1.2) / 2.4)
    for i, (label, value, color, target) in enumerate(metrics):
        x = 66 + i * 192
        text(draw, (x, y + 72), label, 11, MUTED, True)
        text(draw, (x, y + 101), value, 23, WHITE, True)
        draw.rounded_rectangle((x, y + 137, x + 158, y + 147), radius=5, fill=GRID)
        draw.rounded_rectangle((x, y + 137, x + int(158 * target * reveal), y + 147), radius=5, fill=color)


def render_frame(frame_number: int) -> Image.Image:
    t = frame_number / FPS
    image = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # Subtle technical grid.
    for x in range(0, WIDTH, 54):
        draw.line((x, 0, x, HEIGHT), fill="#0A1929", width=1)
    for y in range(0, HEIGHT, 54):
        draw.line((0, y, WIDTH, y), fill="#0A1929", width=1)

    intro = ease(t / 1.1)
    draw_header(draw, intro)
    draw_top_flow(image, draw, t)

    decision_active = int((t * 0.8) % 3)
    authority_active = int((t * 0.8 + 1) % 3)
    effect_active = int((t * 0.8 + 2) % 3)

    section(draw, 392, "02", "DECISION PLANE", "PROVE WHAT SHOULD HAPPEN", BLUE,
            [("GROUND", "fresh sources\nprovenance + conflicts"),
             ("PLAN", "typed action\nexpected postconditions"),
             ("SCORE", "impact × reach\nreversibility × confidence")],
            decision_active, ease((t - 0.4) / 0.8))
    section(draw, 626, "03", "AUTHORITY PLANE", "PROVE WHAT MAY HAPPEN", GOLD,
            [("POLICY", "action-level decision\nversioned control"),
             ("APPROVAL", "consequence threshold\nexpiry + alternatives"),
             ("LEASE", "one action · one scope\nshort TTL + revocation")],
            authority_active, ease((t - 0.8) / 0.8))
    section(draw, 860, "04", "EFFECT PLANE", "PROVE WHAT DID HAPPEN", TEAL,
            [("EXECUTE", "idempotency key\nfenced write"),
             ("VERIFY", "independent evidence\ncompound postcondition"),
             ("RECEIPT", "actor · policy · delta\noutcome + recovery")],
            effect_active, ease((t - 1.2) / 0.8))
    draw_recovery_loop(image, draw, t)
    draw_metrics(draw, t)

    # Loop-progress rail.
    p = (t % DURATION_SECONDS) / DURATION_SECONDS
    draw.rectangle((0, HEIGHT - 7, WIDTH, HEIGHT), fill="#10243A")
    draw.rectangle((0, HEIGHT - 7, round(WIDTH * p), HEIGHT), fill=CYAN)
    return image.convert("RGB")


def encode() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total_frames = FPS * DURATION_SECONDS
    with tempfile.TemporaryDirectory(prefix="linkedin-cheatsheet-") as temp_dir:
        frame_dir = Path(temp_dir)
        for index in range(total_frames):
            render_frame(index).save(frame_dir / f"frame-{index:04d}.png", optimize=True)

        poster = render_frame(round(FPS * 3.4))
        poster.save(OUTPUT_DIR / "production-ai-agent-control-cheatsheet-poster.png", optimize=True)

        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
            "-i", str(frame_dir / "frame-%04d.png"), "-c:v", "libx264",
            "-profile:v", "high", "-crf", "19", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(OUTPUT_DIR / "production-ai-agent-control-cheatsheet.mp4"),
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
            "-loop", "0", str(OUTPUT_DIR / "production-ai-agent-control-cheatsheet.gif"),
        ], check=True)

    print(f"rendered dynamic cheatsheet assets in {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    encode()
