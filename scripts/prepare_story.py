#!/usr/bin/env python3
"""Convert import-ready story Markdown into the archive's structured JSON format."""

from __future__ import annotations

import hashlib
import json
import math
import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORIES = ROOT / "stories"
DATA = ROOT / "data"


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("Story must start with front matter")
    _, raw, body = text.split("---\n", 2)
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, body


def inline_markup(value: str) -> str:
    escaped = escape(value, quote=False)
    placeholders: list[str] = []

    def code_repl(match: re.Match[str]) -> str:
        placeholders.append(f"<code>{match.group(1)}</code>")
        return f"\x00{len(placeholders)-1}\x00"

    escaped = re.sub(r"`([^`]+)`", code_repl, escaped)
    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    for index, placeholder in enumerate(placeholders):
        escaped = escaped.replace(f"\x00{index}\x00", placeholder)
    return escaped


def plain_text(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    return re.sub(r"[*_`#>]", "", value).strip()


def markdown_blocks(body: str) -> list[dict[str, str]]:
    lines = body.splitlines()
    blocks: list[dict[str, str]] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        joined = " ".join(part.strip() for part in paragraph).strip()
        paragraph.clear()
        if joined:
            blocks.append({"type": "html", "tag": "p", "html": inline_markup(joined), "text": plain_text(joined)})

    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue
        figure = re.fullmatch(r'!\[(.*?)\]\((\S+)(?:\s+"(.*)")?\)', stripped)
        if figure:
            flush_paragraph()
            blocks.append({"type": "figure", "src": figure.group(2), "alt": figure.group(1), "caption": figure.group(3) or ""})
            index += 1
            continue
        heading = re.match(r"^(#{2,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level = min(3, len(heading.group(1)))
            content = heading.group(2).strip()
            blocks.append({"type": "html", "tag": f"h{level}", "html": inline_markup(content), "text": plain_text(content)})
            index += 1
            continue
        if stripped.startswith("> "):
            flush_paragraph()
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith("> "):
                quote_lines.append(lines[index].strip()[2:])
                index += 1
            quote = " ".join(quote_lines)
            blocks.append({"type": "html", "tag": "blockquote", "html": inline_markup(quote), "text": plain_text(quote)})
            continue
        if re.match(r"^(?:[-*]|\d+\.)\s+", stripped):
            flush_paragraph()
            items: list[str] = []
            ordered = bool(re.match(r"^\d+\.\s+", stripped))
            while index < len(lines):
                current = lines[index].strip()
                match = re.match(r"^(?:[-*]|(\d+)\.)\s+(.+)$", current)
                if not match:
                    break
                marker = f"{match.group(1)}." if ordered and match.group(1) else "•"
                items.append(f"<strong>{marker}</strong> {inline_markup(match.group(2))}")
                index += 1
            text = "\n".join(re.sub(r"<[^>]+>", "", item) for item in items)
            blocks.append({"type": "html", "tag": "p", "html": "<br>".join(items), "text": text})
            continue
        paragraph.append(stripped)
        index += 1
    flush_paragraph()
    return blocks


def prepare(path: Path) -> Path:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    blocks = markdown_blocks(body)
    words = sum(len(block.get("text", "").split()) for block in blocks if block["type"] == "html")
    slug = meta["slug"]
    story = {
        "author": meta.get("author", "Aditya Singh"),
        "blocks": blocks,
        "canonical": meta["canonical"],
        "description": meta["description"],
        "heroAlt": meta.get("hero_alt", ""),
        "heroImage": meta["hero_image"],
        "id": hashlib.sha1(slug.encode()).hexdigest()[:12],
        "modifiedAt": meta["published_at"],
        "publishedAt": meta["published_at"],
        "readTime": f"{math.ceil(words / 200)} min read",
        "slug": slug,
        "sourceUrl": meta["canonical"],
        "subtitle": meta["subtitle"],
        "tags": [item.strip() for item in meta.get("tags", "").split(",") if item.strip()],
        "title": meta["title"],
        "wordCount": words,
    }
    destination = DATA / f"{slug}.json"
    destination.write_text(json.dumps(story, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"prepared {destination.name}: {words} words, {sum(1 for b in blocks if b['type']=='figure')} figures")
    return destination


def main() -> None:
    for path in sorted(STORIES.glob("*.md")):
        if path.name.endswith("-figure-map.md"):
            continue
        prepare(path)


if __name__ == "__main__":
    main()
