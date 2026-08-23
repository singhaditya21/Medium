#!/usr/bin/env python3
"""Shared 2400×1600 deep-dive visual system for the seven-story continuation."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


PAPER = "#F5F7FB"
SURFACE = "#FFFFFF"
INK = "#091631"
MUTED = "#52627A"
LINE = "#C8D2E1"
BLUE = "#1357A6"
BLUE_LIGHT = "#DCEAF8"
TEAL = "#04776E"
TEAL_LIGHT = "#D5EFEB"
GOLD = "#A26808"
GOLD_LIGHT = "#F8E8BE"
RUST = "#AF4237"
RUST_LIGHT = "#F6D8D3"
PURPLE = "#6241A5"
PURPLE_LIGHT = "#E8DFF7"
GREEN = "#2E7D4F"
GREEN_LIGHT = "#DAEEDD"
WHITE = "#FFFFFF"


@dataclass(frozen=True)
class FigureSpec:
    number: int
    title: str
    form: str
    takeaway: str
    domain: str
    insights: tuple[str, str, str]
    contract: tuple[tuple[str, str], tuple[str, str], tuple[str, str]]
    assumption: str = "Reference architecture; no observed production data."
    core: bool = True


@dataclass
class FigureSystem:
    slug: str
    out: Path
    map_path: Path
    story_title: str
    specs: list[FigureSpec]
    footer: str = "AI-assisted design · reference architecture / synthetic values · not production data"
    by_number: dict[int, FigureSpec] = field(init=False)

    def __post_init__(self) -> None:
        self.by_number = {spec.number: spec for spec in self.specs}
        expected = list(range(1, len(self.specs) + 1))
        if sorted(self.by_number) != expected:
            raise ValueError(f"figure numbers must be contiguous: {expected}")

    @staticmethod
    def wrap(value: str, width: int = 24) -> str:
        return "\n".join(textwrap.wrap(value, width=width))

    def chip(self, fig, x: float, y: float, width: float, label: str, value: str, color: str) -> None:
        fig.add_artist(FancyBboxPatch((x, y), width, .024, transform=fig.transFigure,
                                      boxstyle="round,pad=.0015,rounding_size=.003",
                                      facecolor=WHITE, edgecolor=color, linewidth=.75))
        fig.text(x + .006, y + .012, f"{label}  {value}", va="center", color=color,
                 fontsize=6.4, fontweight="bold")

    def sidecar(self, fig, spec: FigureSpec) -> None:
        rail = fig.add_axes([.765, .075, .21, .755])
        rail.set_xlim(0, 100)
        rail.set_ylim(0, 100)
        rail.axis("off")
        rail.text(3, 97, spec.domain, color=BLUE, fontsize=8.5, fontweight="bold", va="center")
        rail.plot([3, 97], [94, 94], color=BLUE, lw=1.2)

        def panel(y, height, title, edge, fill):
            rail.add_patch(FancyBboxPatch((1, y), 98, height, boxstyle="round,pad=.22,rounding_size=1.5",
                                          facecolor=fill, edgecolor=edge, linewidth=.85))
            rail.add_patch(Rectangle((1, y + height - 5), 98, 5, facecolor=edge, edgecolor="none", alpha=.12))
            rail.text(5, y + height - 2.5, title, color=edge, fontsize=7.0, fontweight="bold", va="center")

        panel(76, 16, "DECISION TAKEAWAY", BLUE, "#F7FAFE")
        rail.text(5, 83, self.wrap(spec.takeaway, 42), color=INK, fontsize=7.0, va="center", linespacing=1.18)
        panel(43, 31, "TECHNICAL READING", TEAL, "#F5FBFA")
        for i, insight in enumerate(spec.insights, 1):
            y = 66 - (i - 1) * 8.5
            rail.add_patch(Circle((7, y), 2.1, facecolor=WHITE, edgecolor=TEAL, linewidth=.8))
            rail.text(7, y, str(i), ha="center", va="center", color=TEAL, fontsize=6.1, fontweight="bold")
            rail.text(12, y, self.wrap(insight, 38), color=INK, fontsize=6.7, va="center", linespacing=1.12)
        panel(18, 23, "CONTROL CONTRACT", GOLD, "#FFFBF3")
        for i, (label, value) in enumerate(spec.contract):
            y = 32.5 - i * 6.5
            rail.text(5, y, label, color=GOLD, fontsize=6.2, fontweight="bold", va="center")
            rail.text(96, y, value, color=INK, fontsize=6.5, ha="right", va="center")
            if i < 2:
                rail.plot([5, 96], [y - 3.1, y - 3.1], color=LINE, lw=.5)
        panel(1, 15, "INPUTS / LIMITS", PURPLE, "#FAF8FE")
        rail.text(5, 7.3, self.wrap(spec.assumption, 42), color=INK, fontsize=6.4, va="center", linespacing=1.12)

    def setup(self, number: int, subtitle: str, plot: bool = False):
        spec = self.by_number[number]
        fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
        fig.patch.set_facecolor(PAPER)
        ax.set_facecolor(SURFACE)
        fig.subplots_adjust(left=.055, right=.745, top=.82, bottom=.10)
        fig.text(.035, .968, f"FIGURE {number:02d}", color=BLUE, fontsize=8.0, fontweight="bold")
        fig.text(.035, .925, spec.title, color=INK, fontsize=19.5, fontweight="bold")
        fig.text(.035, .889, subtitle, color=MUTED, fontsize=8.4)
        self.chip(fig, .035, .846, .172, "DOMAIN", spec.domain, BLUE)
        self.chip(fig, .213, .846, .092, "TIER", "CORE" if spec.core else "SUPPLEMENTAL", TEAL)
        self.chip(fig, .311, .846, .145, "FORM", spec.form.upper(), PURPLE)
        self.chip(fig, .462, .846, .205, "EVIDENCE", "SYNTHETIC / REFERENCE", GOLD)
        self.sidecar(fig, spec)
        fig.text(.055, .032, "LEGEND", color=INK, fontsize=6.2, fontweight="bold", va="center")
        x = .105
        for color, label in [(BLUE, "trusted / observed"), (TEAL, "governed / verified"),
                             (GOLD, "decision / review"), (RUST, "risk / failed")]:
            fig.add_artist(Circle((x, .032), .0035, transform=fig.transFigure, facecolor=color, edgecolor=color))
            fig.text(x + .006, .032, label, color=MUTED, fontsize=6.0, va="center")
            x += .12
        fig.text(.975, .032, self.footer, ha="right", color=MUTED, fontsize=5.8, va="center")
        if not plot:
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 90)
            ax.axis("off")
        return fig, ax

    def save(self, fig, number: int) -> None:
        self.out.mkdir(parents=True, exist_ok=True)
        fig.savefig(self.out / f"figure-{number:02d}.png", facecolor=PAPER, dpi=200)
        plt.close(fig)

    def write_map(self) -> None:
        lines = [
            f"# Figure map — {self.story_title}", "",
            "All quantitative values are synthetic. Diagrams are reference architectures, not claims about a deployed system.", "",
            "Renderer: reproducible Matplotlib PNG at 2400×1600. Each figure includes a technical analysis rail, control contract, assumptions, semantic legend, and evidence label.", "",
            "| Figure | Tier | Analytical question / form | Supported takeaway | Inputs / assumptions |",
            "|---:|---|---|---|---|",
        ]
        for spec in self.specs:
            lines.append(f"| {spec.number} | {'Core' if spec.core else 'Supplemental'} | {spec.title} · {spec.form} | {spec.takeaway} | {spec.assumption} |")
        lines.extend(["", "Palette: blue/teal for trusted or verified paths, gold for decisions, rust for risk/failure, and purple for transformation or policy context. Shape, position, and labels duplicate every color encoding.", ""])
        self.map_path.write_text("\n".join(lines), encoding="utf-8")

    def render(self, generators: list[Callable[[], None]]) -> None:
        if len(generators) != len(self.specs):
            raise ValueError("one generator is required per figure spec")
        for generator in generators:
            generator()
        self.write_map()
        print(f"Generated {len(generators)} figures in {self.out}")


def box(ax, x, y, w, h, title, body="", edge=LINE, fill=SURFACE, title_color=INK, fs=8.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.25,rounding_size=.8",
                                facecolor=fill, edgecolor=edge, linewidth=1.05))
    if h >= 10:
        ax.add_patch(Rectangle((x, y + h - 1.3), w, 1.3, facecolor=edge, edgecolor="none", alpha=.13))
    ax.text(x + w * .06, y + h * .66, title, color=title_color, fontsize=fs, fontweight="bold", va="center")
    if body:
        ax.text(x + w * .06, y + h * .30, body, color=MUTED, fontsize=fs - 1.5, va="center", linespacing=1.25)


def arrow(ax, start, end, color=MUTED, lw=1.4, connectionstyle="arc3", style="-|>"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=11, color=color,
                                 linewidth=lw, connectionstyle=connectionstyle))
