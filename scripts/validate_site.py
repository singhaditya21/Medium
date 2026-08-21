#!/usr/bin/env python3
"""Validate story data, generated pages, feeds, and optionally the live Pages site."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlsplit

import requests
from lxml import etree, html

from build_site import DATA_DIR, ROOT, SERIES, SITE_URL, clean_url, load_stories


def local_references(document: html.HtmlElement, page_path: Path) -> Iterable[Path]:
    for node in document.xpath("//*[@href or @src]"):
        value = node.get("href") or node.get("src") or ""
        parts = urlsplit(value)
        if not value or value.startswith("#") or parts.scheme or parts.netloc:
            continue
        path = parts.path
        if not path or path.startswith("mailto:"):
            continue
        candidate = (page_path.parent / path).resolve()
        if path.endswith("/"):
            candidate /= "index.html"
        yield candidate


def validate_generated_html(path: Path, expected_canonical: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing generated page: {path.relative_to(ROOT)}")
        return
    document = html.fromstring(path.read_text(encoding="utf-8"))
    canonical = document.xpath("string(//link[@rel='canonical']/@href)")
    if clean_url(canonical) != clean_url(expected_canonical):
        errors.append(f"canonical mismatch in {path.relative_to(ROOT)}: {canonical}")
    if not document.xpath("//meta[@name='description' and normalize-space(@content)]"):
        errors.append(f"missing meta description: {path.relative_to(ROOT)}")
    if not document.xpath("//script[@type='application/ld+json']"):
        errors.append(f"missing JSON-LD: {path.relative_to(ROOT)}")
    for reference in local_references(document, path):
        try:
            reference.relative_to(ROOT)
        except ValueError:
            errors.append(f"reference escapes repository in {path.relative_to(ROOT)}: {reference}")
            continue
        if not reference.exists():
            errors.append(f"broken local reference in {path.relative_to(ROOT)}: {reference.relative_to(ROOT)}")


def validate_live(stories: list[dict], errors: list[str]) -> None:
    urls = [SITE_URL, f"{SITE_URL}series/", f"{SITE_URL}feed.xml"]
    urls.extend(story["pageUrl"] for story in stories)
    session = requests.Session()
    session.headers["User-Agent"] = "MediumArchiveHealthCheck/1.0"
    for url in urls:
        try:
            response = session.get(url, timeout=30, allow_redirects=True)
            if response.status_code != 200:
                errors.append(f"live URL returned {response.status_code}: {url}")
        except requests.RequestException as exc:
            errors.append(f"live URL failed: {url} ({exc})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="also check deployed GitHub Pages URLs")
    args = parser.parse_args()
    errors: list[str] = []
    stories = load_stories()
    slugs = [story.get("slug", "") for story in stories]
    if len(slugs) != len(set(slugs)):
        errors.append("story slugs are not unique")

    required = {"id", "slug", "title", "canonical", "publishedAt", "blocks"}
    for story in stories:
        missing = sorted(required - set(story))
        if missing:
            errors.append(f"{story.get('slug', '<unknown>')}: missing fields {', '.join(missing)}")
            continue
        figure_index = 0
        for block in story["blocks"]:
            if block.get("type") != "figure":
                continue
            figure_index += 1
            if not block.get("alt", "").strip():
                errors.append(f"{story['slug']} figure {figure_index}: missing alt text")
            if not block.get("caption", "").strip():
                errors.append(f"{story['slug']} figure {figure_index}: missing caption")
            images = list((ROOT / "assets" / "images" / story["slug"]).glob(f"figure-{figure_index:02d}.*"))
            if len(images) != 1 or images[0].stat().st_size < 500:
                errors.append(f"{story['slug']} figure {figure_index}: expected one valid local image")
        validate_generated_html(ROOT / "articles" / story["slug"] / "index.html", story["canonical"], errors)
        story["pageUrl"] = f"{SITE_URL}articles/{story['slug']}/"

    validate_generated_html(ROOT / "index.html", SITE_URL, errors)
    validate_generated_html(ROOT / "series" / "index.html", f"{SITE_URL}series/", errors)
    for series in SERIES:
        unknown = sorted(set(series["stories"]) - set(slugs))
        if unknown:
            errors.append(f"series {series['slug']} references unknown stories: {', '.join(unknown)}")
        validate_generated_html(
            ROOT / "series" / series["slug"] / "index.html",
            f"{SITE_URL}series/{series['slug']}/",
            errors,
        )

    try:
        feed = etree.parse(str(ROOT / "feed.xml"))
        entries = feed.xpath("//*[local-name()='entry']")
        if len(entries) != len(stories):
            errors.append(f"Atom entry count {len(entries)} does not match story count {len(stories)}")
    except (OSError, etree.XMLSyntaxError) as exc:
        errors.append(f"invalid Atom feed: {exc}")
    try:
        rss = etree.parse(str(ROOT / "rss.xml"))
        items = rss.xpath("//item")
        if len(items) != len(stories):
            errors.append(f"RSS item count {len(items)} does not match story count {len(stories)}")
    except (OSError, etree.XMLSyntaxError) as exc:
        errors.append(f"invalid RSS feed: {exc}")
    try:
        json_feed = json.loads((ROOT / "feed.json").read_text(encoding="utf-8"))
        if len(json_feed.get("items", [])) != len(stories):
            errors.append("JSON Feed item count does not match story count")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON Feed: {exc}")

    manifest_path = DATA_DIR / "stories.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if len(manifest) != len(stories):
            errors.append("story manifest count does not match source data")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid story manifest: {exc}")

    if args.live:
        validate_live(stories, errors)
    if errors:
        print("Site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"validated {len(stories)} stories, {len(SERIES)} series, and three feeds" + (" plus live URLs" if args.live else ""))


if __name__ == "__main__":
    main()
