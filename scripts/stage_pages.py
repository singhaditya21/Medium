#!/usr/bin/env python3
"""Stage only public static assets for GitHub Pages deployment."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "_site"
PUBLIC_FILES = [".nojekyll", "index.html", "favicon.ico", "robots.txt", "sitemap.xml", "feed.xml", "rss.xml", "feed.json"]
PUBLIC_DIRECTORIES = ["assets", "articles", "series"]


def main() -> None:
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir()
    for name in PUBLIC_FILES:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, DESTINATION / name)
    for name in PUBLIC_DIRECTORIES:
        source = ROOT / name
        if not source.exists():
            raise SystemExit(f"Missing public directory: {source}")
        shutil.copytree(source, DESTINATION / name)
    print(f"staged public site: {DESTINATION}")


if __name__ == "__main__":
    main()
