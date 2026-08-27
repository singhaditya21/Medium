#!/usr/bin/env python3
"""Validate story data, generated pages, feeds, and optionally the live Pages site."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlsplit

import requests
from lxml import etree, html
from PIL import Image

from build_site import DATA_DIR, ROOT, SERIES, SITE_URL, clean_url, load_stories


TECHNICAL_FIGURE_CONTRACTS = {
    "your-ai-agents-memory-is-a-database-not-a-prompt": {"memory", "provenance", "retrieval", "retention", "evidence", "source", "trust", "freshness", "deletion", "valid time"},
    "every-ai-agent-action-needs-a-receipt": {"receipt", "action", "effect", "verification", "idempotency"},
    "human-approval-is-a-queueing-system": {"approval", "review", "queue", "reviewer", "risk", "evidence"},
    "your-multi-agent-system-is-a-distributed-system": {"agent", "coordination", "distributed", "workflow", "message", "ownership", "fencing", "delivery", "idempotency", "event", "compensation", "split-brain", "lease", "epoch", "worker"},
    "model-routing-is-capital-allocation": {"model", "route", "routing", "cost", "utility", "budget", "capital", "inference"},
    "your-ai-agent-needs-a-real-kill-switch": {"containment", "kill", "revocation", "authority", "recovery", "stop", "enforcement", "effect", "incident", "fencing", "tool", "ambiguity", "idempotency"},
    "do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation": {"evaluation", "evidence", "scenario", "production", "promotion", "failure", "trial", "risk"},
}
TECHNICAL_FIGURE_COUNT = 18
TECHNICAL_FIGURE_COUNTS = {
    "your-ai-agents-memory-is-a-database-not-a-prompt": 18,
    "every-ai-agent-action-needs-a-receipt": 18,
    "human-approval-is-a-queueing-system": 11,
    "your-multi-agent-system-is-a-distributed-system": 11,
    "model-routing-is-capital-allocation": 10,
    "your-ai-agent-needs-a-real-kill-switch": 10,
    "do-not-let-an-ai-agent-touch-production-until-it-passes-this-evaluation": 18,
}
TECHNICAL_FIGURE_SIZE = (2400, 1600)
TECHNICAL_FIGURE_MIN_BYTES = 200_000


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


def validate_technical_figure_html(story: dict, errors: list[str]) -> None:
    path = ROOT / "articles" / story["slug"] / "index.html"
    if not path.exists():
        return
    document = html.fromstring(path.read_text(encoding="utf-8"))
    figures = document.xpath("//figure[contains(concat(' ', normalize-space(@class), ' '), ' story-figure ')]")
    expected_count = TECHNICAL_FIGURE_COUNTS.get(story["slug"], TECHNICAL_FIGURE_COUNT)
    if len(figures) != expected_count:
        errors.append(f"{story['slug']}: generated page has {len(figures)} technical figures, expected {expected_count}")
        return
    for index, figure in enumerate(figures, 1):
        source_number = int(figure.get("data-figure-label", index))
        if figure.get("id") != f"figure-{source_number}":
            errors.append(f"{story['slug']} figure {index}: missing stable figure anchor")
        if figure.get("data-figure-index") != str(index) or figure.get("data-figure-total") != str(expected_count):
            errors.append(f"{story['slug']} figure {index}: invalid dynamic-viewer metadata")
        images = figure.xpath("./div[contains(@class, 'story-figure-frame')]/img")
        captions = figure.xpath("./figcaption")
        toolbars = figure.xpath("./div[contains(@class, 'figure-explorer-toolbar')]")
        controls = figure.xpath("./div[contains(@class, 'figure-explorer-toolbar')]//button[@data-figure-open]")
        if len(images) != 1 or len(captions) != 1 or len(toolbars) != 1 or len(controls) != 1:
            errors.append(f"{story['slug']} figure {index}: incomplete interactive figure structure")
            continue
        if controls[0].get("hidden") is None or not controls[0].get("aria-label"):
            errors.append(f"{story['slug']} figure {index}: progressive-enhancement control is not safely initialized")
        image = images[0]
        caption_id = f"figure-{source_number}-caption"
        if captions[0].get("id") != caption_id or image.get("aria-describedby") != caption_id:
            errors.append(f"{story['slug']} figure {index}: caption is not programmatically associated")
        if (image.get("width"), image.get("height")) != tuple(map(str, TECHNICAL_FIGURE_SIZE)):
            errors.append(f"{story['slug']} figure {index}: missing intrinsic 2400x1600 dimensions")


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
        technical_terms = TECHNICAL_FIGURE_CONTRACTS.get(story["slug"])
        figure_blocks = [block for block in story["blocks"] if block.get("type") == "figure"]
        expected_count = TECHNICAL_FIGURE_COUNTS.get(story["slug"], TECHNICAL_FIGURE_COUNT)
        if technical_terms and len(figure_blocks) != expected_count:
            errors.append(f"{story['slug']}: expected {expected_count} technical figures, found {len(figure_blocks)}")
        figure_index = 0
        figure_alts: set[str] = set()
        figure_captions: set[str] = set()
        for block in story["blocks"]:
            if block.get("type") != "figure":
                continue
            figure_index += 1
            alt = block.get("alt", "").strip()
            caption = block.get("caption", "").strip()
            if not alt:
                errors.append(f"{story['slug']} figure {figure_index}: missing alt text")
            if not caption:
                errors.append(f"{story['slug']} figure {figure_index}: missing caption")
            source_path = Path(urlsplit(block.get("src", "")).path)
            source_number_match = re.search(r"figure-(\d+)", source_path.stem, re.I)
            source_number = int(source_number_match.group(1)) if source_number_match else figure_index
            local_source = (ROOT / source_path).resolve()
            if local_source.is_relative_to(ROOT) and local_source.exists():
                images = [local_source]
            else:
                images = list(
                    (ROOT / "assets" / "images" / story["slug"]).glob(
                        f"figure-{source_number:02d}.*"
                    )
                )
            if len(images) != 1 or images[0].stat().st_size < 500:
                errors.append(f"{story['slug']} figure {figure_index}: expected one valid local image")
            if technical_terms:
                normalized = f"{alt} {caption}".casefold()
                if len(alt.split()) < 8:
                    errors.append(f"{story['slug']} figure {figure_index}: alt text is not technically descriptive")
                if not caption.startswith(f"Figure {source_number}."):
                    errors.append(f"{story['slug']} figure {figure_index}: caption does not match its source figure number")
                if not any(term in normalized for term in technical_terms):
                    errors.append(f"{story['slug']} figure {figure_index}: content does not match the story-specific relevance vocabulary")
                if alt.casefold() in figure_alts or caption.casefold() in figure_captions:
                    errors.append(f"{story['slug']} figure {figure_index}: duplicate figure description")
                figure_alts.add(alt.casefold())
                figure_captions.add(caption.casefold())
                if len(images) == 1:
                    if images[0].suffix.casefold() != ".png" or images[0].stat().st_size < TECHNICAL_FIGURE_MIN_BYTES:
                        errors.append(f"{story['slug']} figure {figure_index}: full-resolution PNG is below the technical-detail floor")
                    try:
                        with Image.open(images[0]) as source_image:
                            if source_image.size != TECHNICAL_FIGURE_SIZE:
                                errors.append(f"{story['slug']} figure {figure_index}: expected {TECHNICAL_FIGURE_SIZE}, found {source_image.size}")
                    except OSError as exc:
                        errors.append(f"{story['slug']} figure {figure_index}: invalid image ({exc})")
        validate_generated_html(ROOT / "articles" / story["slug"] / "index.html", story["canonical"], errors)
        if technical_terms:
            validate_technical_figure_html(story, errors)
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
