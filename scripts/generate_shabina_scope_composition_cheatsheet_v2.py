#!/usr/bin/env python3
"""Render the premium motion narrative for scope attenuation and composed-action safety."""

from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "images" / "linkedin-shabina-scope-composition-cheatsheet-v2"
WIDTH, HEIGHT = 1080, 1350
FPS = 15
DURATION = 24.0
TRANSITION = 0.45

WHITE = "#FFFFFF"
INK = "#071426"
BLUE = "#075BDA"
ELECTRIC = "#147BFF"
DEEP_BLUE = "#003D99"
PALE = "#EAF3FF"
PALE_2 = "#F5F9FF"
LINE = "#B7D2F5"
GRID = "#EDF4FD"

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_MONO = Path("/System/Library/Fonts/SFNSMono.ttf")
FONT_MATH = Path("/System/Library/Fonts/Supplemental/STIXGeneral.otf")
FONT_MATH_BOLD = Path("/System/Library/Fonts/Supplemental/STIXGeneralBol.otf")

SCENE_EDGES = (0.0, 3.4, 7.6, 11.8, 16.0, 20.1, 24.0)
SCENE_LABELS = ("BOUNDARY", "CAPABILITY", "CLOCKS", "COMPOSITION", "LEASE", "RECEIPT")


def font(size: int, bold: bool = False, mono: bool = False, math_font: bool = False) -> ImageFont.FreeTypeFont:
    if math_font:
        path = FONT_MATH_BOLD if bold and FONT_MATH_BOLD.exists() else FONT_MATH
    elif mono:
        path = FONT_MONO
    else:
        path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size)


def smooth(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def phase(progress: float, start: float, end: float) -> float:
    if end <= start:
        return 1.0
    return smooth((progress - start) / (end - start))


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def mix_color(a: str, b: str, amount: float) -> tuple[int, int, int]:
    av, bv = rgb(a), rgb(b)
    return tuple(round(x + (y - x) * amount) for x, y in zip(av, bv))


def text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], value: str, size: int,
         color: str = INK, bold: bool = False, anchor: str | None = None,
         mono: bool = False, math_font: bool = False) -> None:
    draw.text(xy, value, font=font(size, bold, mono, math_font), fill=color, anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: int = 20,
            fill: str | tuple[int, int, int] = WHITE, outline: str = LINE, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def glow(image: Image.Image, center: tuple[float, float], radius: int, strength: float = 1.0) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse((x - radius, y - radius, x + radius, y + radius),
              fill=(*rgb(ELECTRIC), round(65 * strength)))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius / 2)))


def line_arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float],
               progress: float = 1.0, width: int = 4, color: str = BLUE,
               dashed: bool = False) -> tuple[float, float]:
    progress = max(0.0, min(1.0, progress))
    x1, y1 = start
    x2, y2 = end
    ex = x1 + (x2 - x1) * progress
    ey = y1 + (y2 - y1) * progress
    if dashed:
        segments = 16
        for index in range(0, segments, 2):
            a = index / segments
            b = min(progress, (index + 1) / segments)
            if a >= progress:
                break
            draw.line((x1 + (x2 - x1) * a, y1 + (y2 - y1) * a,
                       x1 + (x2 - x1) * b, y1 + (y2 - y1) * b), fill=color, width=width)
    else:
        draw.line((x1, y1, ex, ey), fill=color, width=width)
    if progress > 0.96:
        angle = math.atan2(y2 - y1, x2 - x1)
        length = 13
        wing = 0.52
        draw.polygon([
            (x2, y2),
            (x2 - length * math.cos(angle - wing), y2 - length * math.sin(angle - wing)),
            (x2 - length * math.cos(angle + wing), y2 - length * math.sin(angle + wing)),
        ], fill=color)
    return ex, ey


def pulse_dot(image: Image.Image, draw: ImageDraw.ImageDraw, start: tuple[float, float],
              end: tuple[float, float], position: float, radius: int = 6) -> None:
    x = start[0] + (end[0] - start[0]) * position
    y = start[1] + (end[1] - start[1]) * position
    glow(image, (x, y), radius * 3, 0.7)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=ELECTRIC)


def check(draw: ImageDraw.ImageDraw, center: tuple[int, int], active: bool = True, radius: int = 15) -> None:
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                 fill=BLUE if active else WHITE, outline=BLUE, width=2)
    color = WHITE if active else BLUE
    draw.line((x - 7, y, x - 2, y + 6, x + 8, y - 7), fill=color, width=3, joint="curve")


def background(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=WHITE)
    for x in range(0, WIDTH + 1, 54):
        draw.line((x, 0, x, HEIGHT), fill=GRID, width=1)
    for y in range(0, HEIGHT + 1, 54):
        draw.line((0, y, WIDTH, y), fill=GRID, width=1)
    draw.polygon([(830, 0), (1080, 0), (1080, 250)], fill=PALE_2)


def top_chrome(draw: ImageDraw.ImageDraw, scene_index: int, global_progress: float) -> None:
    rounded(draw, (52, 37, 304, 73), 18, PALE_2, BLUE, 2)
    text(draw, (178, 55), "AUTHORIZATION DEEP DIVE", 15, BLUE, True, "mm")
    rounded(draw, (810, 37, 1028, 73), 18, WHITE, BLUE, 2)
    text(draw, (919, 55), "SHABINA × ADITYA", 15, BLUE, True, "mm")
    y = 98
    for index, label in enumerate(SCENE_LABELS):
        x1 = 52 + index * 164
        active = index == scene_index
        complete = index < scene_index
        draw.line((x1, y, x1 + 128, y), fill=BLUE if complete or active else LINE,
                  width=5 if active else 3)
        text(draw, (x1, y + 15), f"0{index + 1}  {label}", 12,
             BLUE if complete or active else DEEP_BLUE, active)
    draw.rectangle((0, HEIGHT - 8, WIDTH, HEIGHT), fill=PALE)
    draw.rectangle((0, HEIGHT - 8, round(WIDTH * global_progress), HEIGHT), fill=BLUE)


def scene_header(draw: ImageDraw.ImageDraw, eyebrow: str, title_lines: tuple[str, ...],
                 subtitle: str, title_size: int = 50) -> None:
    text(draw, (54, 145), eyebrow, 16, BLUE, True)
    y = 182
    for index, line in enumerate(title_lines):
        text(draw, (54, y + index * (title_size + 5)), line, title_size,
             BLUE if index == len(title_lines) - 1 and len(title_lines) > 1 else INK, True)
    subtitle_y = y + len(title_lines) * (title_size + 5) + 10
    text(draw, (54, subtitle_y), subtitle, 21, INK)
    draw.line((54, subtitle_y + 42, 1026, subtitle_y + 42), fill=BLUE, width=4)


def scope_node(draw: ImageDraw.ImageDraw, image: Image.Image, x: int, y: int,
               label: str, width: int, active: bool, caption: str) -> None:
    if active:
        glow(image, (x, y), 43, 0.9)
    draw.ellipse((x - 36, y - 36, x + 36, y + 36), fill=PALE_2,
                 outline=ELECTRIC if active else BLUE, width=4)
    text(draw, (x, y), label, 22, BLUE, True, "mm")
    text(draw, (x, y + 57), caption, 15, INK, True, "mm")
    draw.rounded_rectangle((x - width / 2, y + 83, x + width / 2, y + 99), radius=8, fill=BLUE)


def draw_boundary(image: Image.Image, draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_header(draw, "THE ARCHITECTURAL BOUNDARY", ("NARROWER PERMISSIONS ≠", "SAFER OUTCOMES"),
                 "Delegation safety and composed-action safety are different control problems.", 52)
    top = 402
    rounded(draw, (54, top, 514, 1044), 28, WHITE, LINE, 2)
    rounded(draw, (566, top, 1026, 1044), 28, WHITE, LINE, 2)
    text(draw, (84, top + 39), "RUNTIME CONTROL", 17, BLUE, True)
    text(draw, (84, top + 73), "Can authority expand across a hop?", 23, INK, True)
    text(draw, (84, top + 107), "Cryptographic capability attenuation", 18, BLUE)

    ys = top + 224
    xs = (112, 232, 352, 462)
    widths = (108, 84, 62, 42)
    captions = ("OWNER", "AGENT", "CRM", "BILLING")
    build = phase(p, 0.06, 0.58)
    for index, (x, width, caption) in enumerate(zip(xs, widths, captions)):
        node_p = phase(build, index * 0.18, index * 0.18 + 0.22)
        if node_p > 0:
            scope_node(draw, image, x, ys, f"S{index}", width, node_p > 0.76, caption)
        if index < len(xs) - 1:
            ap = phase(build, index * 0.18 + 0.10, index * 0.18 + 0.30)
            line_arrow(draw, (x + 42, ys), (xs[index + 1] - 42, ys), ap, 4)
    rounded(draw, (84, top + 382, 484, top + 468), 18, PALE_2, BLUE, 2)
    text(draw, (284, top + 416), "S[i+1] ⊆ S[i]", 32, INK, True, "mm", math_font=True)
    text(draw, (284, top + 450), "permission may only narrow", 16, BLUE, True, "mm")
    text(draw, (84, top + 516), "Necessary", 18, BLUE, True)
    text(draw, (84, top + 551), "Blocks ambient scope expansion.", 20, INK)
    text(draw, (84, top + 590), "Not sufficient", 18, BLUE, True)
    text(draw, (84, top + 613), "Permitted effects can still compose.", 20, INK)

    text(draw, (596, top + 39), "PLANNING CONTROL", 17, BLUE, True)
    text(draw, (596, top + 73), "Can allowed actions combine unsafely?", 23, INK, True)
    text(draw, (596, top + 107), "Effect graph + consequence budget", 18, BLUE)
    action_x, graph_x, risk_x = 646, 805, 955
    action_ys = (top + 206, top + 294, top + 382)
    actions = (("A1", "CRM Δ"), ("A2", "Priority Δ"), ("A3", "SLA Δ"))
    converge = phase(p, 0.22, 0.82)
    for index, ((label, body), ay) in enumerate(zip(actions, action_ys)):
        rounded(draw, (596, ay - 33, 704, ay + 33), 14, PALE_2, BLUE, 2)
        text(draw, (622, ay), label, 15, BLUE, True, "mm")
        text(draw, (674, ay), body, 15, INK, True, "mm")
        line_arrow(draw, (709, ay), (770, top + 294), phase(converge, index * 0.08, 0.58), 3)
    rounded(draw, (772, top + 238, 872, top + 350), 20, PALE, BLUE, 3)
    text(draw, (822, top + 275), "EFFECT", 15, BLUE, True, "mm")
    text(draw, (822, top + 311), "GRAPH", 19, INK, True, "mm")
    line_arrow(draw, (878, top + 294), (916, top + 294), phase(converge, 0.52, 0.76), 4)
    rounded(draw, (918, top + 232, 1000, top + 356), 20, WHITE, BLUE, 3)
    text(draw, (959, top + 268), "Rcomp", 17, BLUE, True, "mm")
    text(draw, (959, top + 309), "> B?", 28, INK, True, "mm")
    text(draw, (959, top + 339), "HOLD", 14, BLUE, True, "mm")
    if converge > 0.08:
        pulse_dot(image, draw, (710, action_ys[0]), (770, top + 294), (p * 1.8) % 1.0, 5)
    rounded(draw, (596, top + 487, 996, top + 627), 20, PALE_2, LINE, 2)
    text(draw, (622, top + 520), "KEY INSIGHT", 16, BLUE, True)
    text(draw, (622, top + 561), "Every hop can pass—", 25, INK, True)
    text(draw, (622, top + 599), "while the transaction fails.", 25, BLUE, True)


def draw_capability(image: Image.Image, draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_header(draw, "01 / CRYPTOGRAPHIC CAPABILITY CHAIN", ("VERIFY EVERY HOP.",),
                 "Authority is attenuated, audience-bound, time-bound and lineage-verifiable.", 52)
    top = 360
    names = (("C0", "OWNER", "root grant"), ("C1", "AGENT", "delegated"),
             ("C2", "CRM", "tool-bound"), ("C3", "BILLING", "action-bound"))
    xs = (120, 390, 660, 930)
    for index, ((cap, who, desc), x) in enumerate(zip(names, xs)):
        active = int(min(3, p * 4.6)) == index
        if active:
            glow(image, (x, top + 95), 55, 0.85)
        rounded(draw, (x - 92, top, x + 92, top + 190), 22,
                PALE if active else WHITE, ELECTRIC if active else LINE, 3 if active else 2)
        text(draw, (x, top + 42), cap, 27, BLUE, True, "mm")
        text(draw, (x, top + 91), who, 18, INK, True, "mm")
        text(draw, (x, top + 127), desc, 16, BLUE, False, "mm")
        text(draw, (x, top + 163), f"depth={index}", 15, INK, False, "mm", mono=True)
        if index < 3:
            ap = phase(p, index * 0.12 + 0.10, index * 0.12 + 0.32)
            line_arrow(draw, (x + 98, top + 95), (xs[index + 1] - 98, top + 95), ap, 4)
            if ap > 0.2:
                pulse_dot(image, draw, (x + 98, top + 95), (xs[index + 1] - 98, top + 95),
                          (p * 2.2 + index * 0.21) % 1.0, 5)

    rounded(draw, (54, 590, 1026, 922), 26, PALE_2, LINE, 2)
    text(draw, (82, 626), "PER-HOP VALIDATOR", 18, BLUE, True)
    checks = (
        ("SIGNATURE", "verify(sig[i], issuer_key)"),
        ("SCOPE", "scope[i+1] ⊆ scope[i]"),
        ("AUDIENCE", "aud[i+1] = intended_tool"),
        ("EXPIRY", "exp[i+1] ≤ exp[i]"),
        ("LINEAGE", "parent_jti[i+1] = jti[i]"),
        ("DEPTH", "depth[i+1] ≤ max_depth"),
    )
    for index, (label, value) in enumerate(checks):
        col, row = index % 2, index // 2
        x = 82 + col * 470
        y = 686 + row * 78
        done = p > 0.13 + index * 0.09
        check(draw, (x + 16, y + 12), done, 14)
        text(draw, (x + 48, y - 2), label, 14, BLUE, True)
        text(draw, (x + 48, y + 26), value, 19, INK, False, math_font=True)

    rounded(draw, (54, 956, 1026, 1198), 26, WHITE, BLUE, 2)
    text(draw, (82, 991), "ATTENUATION FUNCTION", 16, BLUE, True)
    text(draw, (540, 1051), "C[i+1] = Attenuate(C[i], Δ[i])", 33, INK, True, "mm", math_font=True)
    text(draw, (540, 1108), "No child may add scope, extend TTL, change audience or erase ancestry.",
         21, BLUE, True, "mm")
    text(draw, (540, 1152), "Result: least authority is enforced structurally—not requested behaviorally.",
         19, INK, False, "mm")


def clock_icon(draw: ImageDraw.ImageDraw, center: tuple[int, int], angle: float,
               active: bool = False) -> None:
    x, y = center
    draw.ellipse((x - 30, y - 30, x + 30, y + 30), fill=WHITE,
                 outline=ELECTRIC if active else BLUE, width=4)
    draw.line((x, y, x + 17 * math.cos(angle), y + 17 * math.sin(angle)), fill=BLUE, width=4)
    draw.line((x, y, x + 11 * math.cos(angle * -0.53), y + 11 * math.sin(angle * -0.53)),
              fill=INK, width=3)
    draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=BLUE)


def draw_clocks(image: Image.Image, draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_header(draw, "02 / THREE-CLOCK GOVERNANCE", ("DRIFT CHANGES ADMISSIBILITY.",),
                 "Structure, evidence and execution are evaluated on different clocks.", 48)
    card_y = 360
    clocks = (
        ("EVENT-TIME", "Graph or ownership changed", "SUSPEND NOW"),
        ("ATTESTATION-TIME", "Conditions need fresh proof", "REVALIDATE"),
        ("EXECUTION-TIME", "Action is about to run", "RECHECK"),
    )
    active_clock = min(2, int(p * 3.5))
    for index, (heading, detail, command) in enumerate(clocks):
        x1 = 54 + index * 324
        active = active_clock == index
        if active:
            glow(image, (x1 + 55, card_y + 82), 42, 0.75)
        rounded(draw, (x1, card_y, x1 + 296, card_y + 220), 24,
                PALE if active else WHITE, ELECTRIC if active else LINE, 3 if active else 2)
        clock_icon(draw, (x1 + 58, card_y + 75), p * 8 + index, active)
        text(draw, (x1 + 104, card_y + 47), heading, 17, INK, True)
        text(draw, (x1 + 25, card_y + 132), detail, 17, INK)
        text(draw, (x1 + 25, card_y + 177), command, 18, BLUE, True)

    text(draw, (54, 635), "AUTHORIZATION STATE MACHINE", 17, BLUE, True)
    states = ("ACTIVE", "SUSPENDED", "RE-ATTESTED", "ADMISSIBLE")
    xs = (132, 398, 674, 950)
    current = min(3, int(p * 4.2))
    for index, (label, x) in enumerate(zip(states, xs)):
        active = current == index
        if active:
            glow(image, (x, 753), 52, 0.8)
        draw.ellipse((x - 61, 692, x + 61, 814), fill=PALE if active else WHITE,
                     outline=ELECTRIC if active else BLUE, width=4 if active else 2)
        text(draw, (x, 753), label, 16 if label != "RE-ATTESTED" else 14,
             INK if not active else BLUE, True, "mm")
        if index < 3:
            ap = phase(p, index * 0.18 + 0.10, index * 0.18 + 0.30)
            line_arrow(draw, (x + 69, 753), (xs[index + 1] - 69, 753), ap, 4)
    labels = ("structure Δ", "proof refreshed", "pre-action check")
    for index, label in enumerate(labels):
        text(draw, ((xs[index] + xs[index + 1]) / 2, 827), label, 14, BLUE, True, "mm")

    rounded(draw, (54, 888, 1026, 1136), 26, PALE_2, LINE, 2)
    text(draw, (82, 924), "CHAIN-LENGTH-ADJUSTED RE-ATTESTATION", 17, BLUE, True)
    text(draw, (540, 994), "T_att(n,σ) = T0 / [1 + α(n−1) + βσ]", 34, INK, True, "mm", math_font=True)
    text(draw, (540, 1053), "Longer chain or higher drift volatility ⇒ shorter validation interval.",
         21, BLUE, True, "mm", math_font=True)
    text(draw, (540, 1097), "Event-time can suspend authority before the next scheduled attestation.",
         18, INK, False, "mm")


def action_box(draw: ImageDraw.ImageDraw, x: int, y: int, key: str, title: str, value: str,
               active: bool) -> None:
    rounded(draw, (x, y, x + 238, y + 116), 20, PALE if active else WHITE,
            ELECTRIC if active else LINE, 3 if active else 2)
    text(draw, (x + 22, y + 24), key, 15, BLUE, True)
    text(draw, (x + 22, y + 53), title, 18, INK, True)
    text(draw, (x + 22, y + 87), value, 17, BLUE, False, mono=True)


def draw_composition(image: Image.Image, draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_header(draw, "03 / COMPOSED-EFFECT GRAPH", ("EACH ACTION PASSES.", "THE TRANSACTION DOES NOT."),
                 "Example transaction: individually permitted changes create a coupled consequence.", 46)
    top = 430
    actions = (("A1", "Price override", "+12%"), ("A2", "Service priority", "P3 → P1"),
               ("A3", "Customer SLA", "4 hours"))
    action_ys = (top, top + 166, top + 332)
    for index, ((key, title, value), y) in enumerate(zip(actions, action_ys)):
        active = p > index * 0.14
        action_box(draw, 54, y, key, title, value, active)
        check(draw, (267, y + 26), active, 13)

    effect_nodes = (("MARGIN", 480, top + 45), ("CAPACITY", 480, top + 211),
                    ("COMMITMENT", 480, top + 377))
    for index, (label, x, y) in enumerate(effect_nodes):
        active = p > 0.28 + index * 0.10
        rounded(draw, (x - 91, y - 43, x + 91, y + 43), 18,
                PALE if active else WHITE, ELECTRIC if active else LINE, 3 if active else 2)
        text(draw, (x, y), label, 16, BLUE if active else INK, True, "mm")
        line_arrow(draw, (298, action_ys[index] + 58), (385, y), phase(p, 0.14 + index * 0.08, 0.42 + index * 0.08), 4)

    hub = (704, top + 211)
    rounded(draw, (620, hub[1] - 76, 788, hub[1] + 76), 24, PALE_2, BLUE, 3)
    text(draw, (704, hub[1] - 27), "EFFECT", 17, BLUE, True, "mm")
    text(draw, (704, hub[1] + 10), "GRAPH", 24, INK, True, "mm")
    text(draw, (704, hub[1] + 48), "cross-coupled", 15, BLUE, False, "mm")
    for index, (_, x, y) in enumerate(effect_nodes):
        line_arrow(draw, (x + 96, y), (616, hub[1]), phase(p, 0.40 + index * 0.06, 0.68 + index * 0.06), 3)

    risk_p = phase(p, 0.60, 0.88)
    line_arrow(draw, (794, hub[1]), (846, hub[1]), risk_p, 4)
    if risk_p > 0.5:
        glow(image, (930, hub[1]), 65, 0.75)
    rounded(draw, (850, hub[1] - 86, 1012, hub[1] + 86), 24, PALE if risk_p > 0.5 else WHITE,
            ELECTRIC if risk_p > 0.5 else LINE, 4 if risk_p > 0.5 else 2)
    text(draw, (931, hub[1] - 42), "COMPOSITE", 15, BLUE, True, "mm")
    text(draw, (931, hub[1] - 8), "RISK >", 24, INK, True, "mm")
    text(draw, (931, hub[1] + 28), "BUDGET", 24, BLUE, True, "mm")
    text(draw, (931, hub[1] + 61), "HOLD", 15, INK, True, "mm")

    rounded(draw, (54, 982, 1026, 1212), 26, WHITE, BLUE, 2)
    text(draw, (82, 1018), "ILLUSTRATIVE COMPOSITE-RISK FUNCTIONAL", 16, BLUE, True)
    text(draw, (540, 1077), "Rcomp = 1 − ∏(1−r[i]) + λX·X + λI·I + λD·D + λC·C", 30,
         INK, True, "mm", math_font=True)
    text(draw, (540, 1131), "X cross-domain · I irreversibility · D propagation depth · C correlation",
         19, BLUE, True, "mm")
    text(draw, (540, 1174), "This is a proposed control functional—not an observed AuthHub metric.",
         18, INK, False, "mm")


def gate_row(draw: ImageDraw.ImageDraw, y: int, label: str, value: str, active: bool) -> None:
    check(draw, (92, y), active, 14)
    text(draw, (125, y - 15), label, 15, BLUE, True)
    text(draw, (125, y + 14), value, 18, INK, False)


def draw_lease(image: Image.Image, draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_header(draw, "04 / ACTION-LEVEL PERMISSION LEASE", ("AUTHORIZE THE CONSEQUENCE.",),
                 "Issue bounded authority only after scope, freshness, risk and recovery agree.", 49)
    top = 365
    rounded(draw, (54, top, 420, 958), 26, PALE_2, LINE, 2)
    text(draw, (82, top + 38), "POLICY DECISION INPUTS", 17, BLUE, True)
    gates = (
        ("SCOPE", "all descendant scopes narrow"),
        ("FRESHNESS", "three-clock evidence current"),
        ("COMPOSITION", "Rcomp ≤ consequence budget"),
        ("POSTCONDITIONS", "compound effects declared"),
        ("RECOVERY", "revoke/compensate admissible"),
    )
    for index, (label, value) in enumerate(gates):
        gate_row(draw, top + 108 + index * 91, label, value, p > 0.07 + index * 0.10)

    pdp_active = p > 0.48
    if pdp_active:
        glow(image, (510, top + 296), 62, 0.8)
    draw.polygon([(446, top + 296), (510, top + 216), (574, top + 296), (510, top + 376)],
                 fill=PALE if pdp_active else WHITE, outline=ELECTRIC if pdp_active else BLUE)
    text(draw, (510, top + 280), "PDP", 22, INK, True, "mm")
    text(draw, (510, top + 318), "ALLOW?", 16, BLUE, True, "mm")
    line_arrow(draw, (422, top + 296), (442, top + 296), phase(p, 0.42, 0.56), 4)
    line_arrow(draw, (578, top + 296), (610, top + 296), phase(p, 0.56, 0.69), 4)

    rounded(draw, (614, top, 1026, 958), 26, WHITE, BLUE, 3)
    text(draw, (644, top + 37), "ILLUSTRATIVE LEASE PAYLOAD", 17, BLUE, True)
    lease_lines = (
        ("subject", '"agent://revops-17"'),
        ("resource", '"crm://account/42"'),
        ("actions", '["update", "commit_sla"]'),
        ("audience", '"crm-prod"'),
        ("ttl", '90s'),
        ("max_depth", '3'),
        ("risk_budget", '0.35'),
        ("parent_jti", '"7f3a…21c9"'),
        ("policy_hash", '"8fd2…a91c"'),
        ("recovery", '"compensate"'),
    )
    reveal = phase(p, 0.55, 0.92)
    for index, (key, value) in enumerate(lease_lines):
        y = top + 78 + index * 48
        visible = reveal > index / len(lease_lines)
        text(draw, (646, y), key, 15, BLUE if visible else LINE, True, mono=True)
        text(draw, (798, y), value, 15, INK if visible else LINE, False, mono=True)
        draw.line((644, y + 23, 996, y + 23), fill=GRID, width=1)
    rounded(draw, (644, top + 536, 996, top + 582), 18, PALE if reveal > 0.85 else PALE_2,
            ELECTRIC if reveal > 0.85 else LINE, 3)
    text(draw, (820, top + 559), "LEASE SEALED · 90s · ACTION-SPECIFIC", 15, BLUE, True, "mm")

    rounded(draw, (54, 992, 1026, 1204), 26, PALE_2, LINE, 2)
    text(draw, (82, 1027), "ALLOW CONDITION", 16, BLUE, True)
    text(draw, (540, 1084), "ALLOW ⇔ scope↓ ∧ fresh(att) ∧ Rcomp≤B ∧ recovery∈A", 31,
         INK, True, "mm", math_font=True)
    text(draw, (540, 1144), "Lease expiry limits exposure; revocation terminates remaining authority.",
         20, BLUE, True, "mm")


def pipeline_node(draw: ImageDraw.ImageDraw, image: Image.Image, x: int, y: int,
                  title: str, sub: str, active: bool) -> None:
    if active:
        glow(image, (x, y), 56, 0.75)
    rounded(draw, (x - 118, y - 68, x + 118, y + 68), 22,
            PALE if active else WHITE, ELECTRIC if active else LINE, 3 if active else 2)
    text(draw, (x, y - 20), title, 19, BLUE if active else INK, True, "mm")
    text(draw, (x, y + 23), sub, 15, INK, False, "mm")


def draw_receipt(image: Image.Image, draw: ImageDraw.ImageDraw, p: float) -> None:
    scene_header(draw, "05 / INDEPENDENT VERIFICATION + RECOVERY", ("DO NOT TRUST THE AGENT'S", "SUCCESS MESSAGE."),
                 "Verify postconditions independently, seal a receipt and recover on failure.", 46)
    y = 490
    nodes = ((190, "EXECUTOR", "runs leased action"), (540, "VERIFIER", "reads source-of-truth"),
             (890, "RECEIPT STORE", "append-only evidence"))
    for index, (x, title, sub) in enumerate(nodes):
        active = min(2, int(p * 3.5)) == index
        pipeline_node(draw, image, x, y, title, sub, active)
        if index < 2:
            line_arrow(draw, (x + 124, y), (nodes[index + 1][0] - 124, y),
                       phase(p, index * 0.18 + 0.10, index * 0.18 + 0.34), 4)
    if p > 0.18:
        pulse_dot(image, draw, (314, y), (416, y), (p * 2.1) % 1.0, 6)
    if p > 0.42:
        pulse_dot(image, draw, (664, y), (766, y), (p * 2.1 + 0.35) % 1.0, 6)

    rounded(draw, (54, 614, 1026, 796), 24, PALE_2, LINE, 2)
    text(draw, (82, 650), "SIGNED ACTION RECEIPT", 16, BLUE, True)
    text(draw, (540, 704), "ρ = H(intent ∥ lease ∥ policy ∥ pre ∥ action ∥ post ∥ verifier ∥ t)", 29,
         INK, True, "mm", math_font=True)
    text(draw, (540, 754), "The evidence binds what was intended, authorized, changed and verified.",
         19, BLUE, True, "mm")

    rounded(draw, (54, 828, 522, 1054), 24, WHITE, BLUE, 2)
    rounded(draw, (558, 828, 1026, 1054), 24, WHITE, BLUE, 2)
    check(draw, (92, 873), p > 0.58, 17)
    text(draw, (126, 858), "POSTCONDITION SATISFIED", 16, BLUE, True)
    text(draw, (84, 922), "COMMIT", 30, INK, True)
    text(draw, (84, 966), "receipt finalised", 18, BLUE)
    text(draw, (84, 1005), "authority expires normally", 17, INK)
    draw.ellipse((579, 856, 613, 890), fill=WHITE, outline=BLUE, width=3)
    text(draw, (596, 873), "!", 20, BLUE, True, "mm")
    text(draw, (630, 858), "POSTCONDITION VIOLATED", 16, BLUE, True)
    text(draw, (588, 922), "REVOKE → COMPENSATE", 27, INK, True)
    text(draw, (588, 966), "verify the recovery action", 18, BLUE)
    text(draw, (588, 1005), "seal linked recovery receipt", 17, INK)

    rounded(draw, (54, 1084, 1026, 1236), 24, PALE, LINE, 2)
    text(draw, (82, 1115), "OPERATING METRICS — DEFINE; DO NOT FABRICATE", 15, BLUE, True)
    metrics = ("revocation p95", "stale execution / 10k", "composite FN rate", "recovery success")
    for index, metric in enumerate(metrics):
        x = 82 + index * 232
        draw.line((x, 1155, x + 28, 1155), fill=BLUE, width=5)
        text(draw, (x, 1181), metric, 16, INK, True)
    text(draw, (540, 1282), "WHERE SHOULD COMPOSED-EFFECT RISK LIVE: PLANNER · PDP · INDEPENDENT SERVICE?",
         17, BLUE, True, "mm")


SCENE_DRAWERS = (draw_boundary, draw_capability, draw_clocks, draw_composition, draw_lease, draw_receipt)


def scene_index_at(t: float) -> tuple[int, float]:
    t = max(0.0, min(DURATION - 1e-6, t))
    for index in range(len(SCENE_EDGES) - 1):
        start, end = SCENE_EDGES[index], SCENE_EDGES[index + 1]
        if start <= t < end:
            return index, (t - start) / (end - start)
    return len(SCENE_DRAWERS) - 1, 1.0


def render_scene(index: int, local_progress: float, global_progress: float) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    background(draw)
    top_chrome(draw, index, global_progress)
    SCENE_DRAWERS[index](image, draw, local_progress)
    text(draw, (54, 1317), "PUBLIC ARCHITECTURE EXCHANGE · 04 SEP 2026 · CONTROL MODEL, NOT PRODUCT CLAIM",
         13, BLUE, True)
    return image.convert("RGB")


def render_frame(t: float) -> Image.Image:
    index, local = scene_index_at(t)
    current = render_scene(index, local, t / DURATION)
    end = SCENE_EDGES[index + 1]
    if index < len(SCENE_DRAWERS) - 1 and end - t < TRANSITION:
        amount = smooth(1.0 - (end - t) / TRANSITION)
        next_image = render_scene(index + 1, 0.0, t / DURATION)
        # A directional wipe preserves typography; a cross-fade makes two dense
        # technical scenes briefly overlap and harms legibility.
        mask = Image.new("L", (WIDTH, HEIGHT), 0)
        mask_draw = ImageDraw.Draw(mask)
        edge = round(WIDTH * (1.0 - amount))
        feather = 54
        if edge + feather < WIDTH:
            mask_draw.rectangle((edge + feather, 0, WIDTH, HEIGHT), fill=255)
        for offset in range(feather):
            if edge + offset >= WIDTH:
                break
            alpha = round(255 * (offset / feather))
            mask_draw.line((edge + offset, 0, edge + offset, HEIGHT), fill=alpha)
        merged = Image.composite(next_image, current, mask)
        merged_draw = ImageDraw.Draw(merged)
        if 0 < edge < WIDTH:
            merged_draw.line((edge, 0, edge, HEIGHT), fill=ELECTRIC, width=4)
        return merged
    return current


def render_storyboard(path: Path) -> None:
    times = (1.8, 5.4, 9.7, 13.8, 18.0, 22.2)
    frames = [render_frame(value).resize((540, 675), Image.Resampling.LANCZOS) for value in times]
    board = Image.new("RGB", (1080, 2025), WHITE)
    for index, frame in enumerate(frames):
        board.paste(frame, ((index % 2) * 540, (index // 2) * 675))
    path.parent.mkdir(parents=True, exist_ok=True)
    board.save(path, optimize=True)


def encode() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mp4_path = OUTPUT_DIR / "scope-composition-control-plane-v2.mp4"
    process = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
        "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(mp4_path),
    ], stdin=subprocess.PIPE)
    assert process.stdin is not None
    total = round(FPS * DURATION)
    for frame_index in range(total):
        process.stdin.write(render_frame(frame_index / FPS).tobytes())
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("ffmpeg MP4 encode failed")

    poster = render_frame(1.7)
    poster.save(OUTPUT_DIR / "scope-composition-control-plane-v2-poster.png", optimize=True)

    palette = OUTPUT_DIR / ".scope-v2-palette.png"
    gif_path = OUTPUT_DIR / "scope-composition-control-plane-v2.gif"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4_path), "-vf",
        "fps=10,scale=720:-1:flags=lanczos,palettegen=max_colors=128", str(palette),
    ], check=True)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4_path), "-i", str(palette),
        "-lavfi", "fps=10,scale=720:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
        "-loop", "0", str(gif_path),
    ], check=True)
    palette.unlink(missing_ok=True)
    print(f"rendered premium V2 package in {OUTPUT_DIR.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard", action="store_true", help="Render six representative frames only")
    parser.add_argument("--storyboard-path", type=Path, default=Path("/tmp/shabina-premium-v2-storyboard.png"))
    args = parser.parse_args()
    if args.storyboard:
        render_storyboard(args.storyboard_path)
        print(args.storyboard_path)
    else:
        encode()


if __name__ == "__main__":
    main()
