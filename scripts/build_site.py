#!/usr/bin/env python3
"""Build a static GitHub Pages archive from the Medium story snapshots in data/."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import requests
from lxml import etree, html as lxml_html
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ARTICLES_DIR = ROOT / "articles"
IMAGE_DIR = ROOT / "assets" / "images"
SITE_URL = "https://singhaditya21.github.io/Medium/"
MEDIUM_PROFILE = "https://medium.com/@singhaditya21_89007"
AUTHOR = "Aditya Singh"
REPOSITORY_URL = "https://github.com/singhaditya21/Medium"
DISCUSSIONS_URL = f"{REPOSITORY_URL}/discussions"

TOPIC_MAP = {
    "a-2-4m-account-is-escalating": ["AI agents", "CRM", "Risk management", "Human-in-the-loop", "Enterprise AI"],
    "ai-agent-identity-is-not-enough": ["AI agents", "Authorization", "Cybersecurity"],
    "what-an-agent-actually-costs": ["AI economics", "FinOps", "Enterprise AI"],
    "enterprise-agent-control-tower": ["Agent governance", "Architecture", "Risk"],
    "agentic-crm-reference-architecture": ["Agentic CRM", "Architecture", "Enterprise AI"],
    "traditional-crm-agentic-ai": ["Agentic CRM", "Strategy", "Transformation"],
    "your-ai-agent-should-not-have-a-standing-role": ["AI agents", "Zero trust", "Authorization", "Cybersecurity", "Enterprise AI"],
}

SERIES = [
    {
        "slug": "production-grade-ai-agents",
        "title": "Production-Grade AI Agents",
        "description": "Identity, authority, evidence, approval, verification, and recovery patterns for agents that act in consequential systems.",
        "stories": [
            "ai-agent-identity-is-not-enough",
            "your-ai-agent-should-not-have-a-standing-role",
            "enterprise-agent-control-tower",
            "a-2-4m-account-is-escalating",
        ],
    },
    {
        "slug": "agentic-crm",
        "title": "Agentic CRM",
        "description": "Reference architectures and operating models for evolving CRM from a passive system of record into a governed system of action.",
        "stories": [
            "traditional-crm-agentic-ai",
            "agentic-crm-reference-architecture",
            "a-2-4m-account-is-escalating",
        ],
    },
    {
        "slug": "ai-unit-economics",
        "title": "AI Unit Economics",
        "description": "Cost models that connect inference, control planes, human review, verification, and business outcomes.",
        "stories": ["what-an-agent-actually-costs"],
    },
]

ALLOWED_INLINE_TAGS = {"a", "strong", "b", "em", "i", "code", "br", "sup", "sub", "s", "mark"}
TRACKING_PARAMS = {"source", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}


def load_stories() -> list[dict[str, Any]]:
    story_paths = [path for path in DATA_DIR.glob("*.json") if path.name != "stories.json"]
    stories = [json.loads(path.read_text(encoding="utf-8")) for path in story_paths]
    for story in stories:
        story["tags"] = story.get("tags") or TOPIC_MAP.get(story["slug"], [])
    return sorted(stories, key=lambda item: item.get("publishedAt", ""), reverse=True)


def date_label(value: str) -> str:
    if not value:
        return ""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.strftime("%d %b %Y").lstrip("0")


def iso_date(value: str) -> str:
    return value[:10] if value else ""


def clean_url(value: str) -> str:
    if not value:
        return value
    parts = urlsplit(value)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k not in TRACKING_PARAMS]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def unwrap(element: etree._Element) -> None:
    parent = element.getparent()
    if parent is None:
        return
    index = parent.index(element)
    if element.text:
        if index == 0:
            parent.text = (parent.text or "") + element.text
        else:
            previous = parent[index - 1]
            previous.tail = (previous.tail or "") + element.text
    for child in list(element):
        element.remove(child)
        parent.insert(index, child)
        index += 1
    if element.tail:
        if index == 0:
            parent.text = (parent.text or "") + element.tail
        else:
            previous = parent[index - 1]
            previous.tail = (previous.tail or "") + element.tail
    parent.remove(element)


def sanitize_inline(fragment: str, base_url: str = MEDIUM_PROFILE) -> str:
    wrapper = lxml_html.fromstring(f"<div>{fragment}</div>")
    for node in list(wrapper.iterdescendants()):
        if not isinstance(node.tag, str):
            node.drop_tree()
            continue
        tag = node.tag.lower()
        if tag not in ALLOWED_INLINE_TAGS:
            unwrap(node)
            continue
        href = clean_url(urljoin(base_url, node.get("href", ""))) if tag == "a" else ""
        node.attrib.clear()
        if tag == "a" and href:
            node.set("href", href)
            node.set("target", "_blank")
            node.set("rel", "noopener noreferrer")
    pieces = [wrapper.text or ""]
    pieces.extend(etree.tostring(child, encoding="unicode", method="html") for child in wrapper)
    return "".join(pieces).strip()


def heading_id(text: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def extension_for(content_type: str, url: str) -> str:
    content_type = content_type.lower().split(";", 1)[0]
    by_type = {
        "image/avif": ".avif",
        "image/gif": ".gif",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/svg+xml": ".svg",
        "image/webp": ".webp",
    }
    if content_type in by_type:
        return by_type[content_type]
    match = re.search(r"\.(avif|gif|jpe?g|png|svg|webp)(?:$|[?#])", url, re.I)
    if not match:
        return ".img"
    suffix = match.group(1).lower()
    return ".jpg" if suffix in {"jpg", "jpeg"} else f".{suffix}"


def download_image(session: requests.Session, url: str, story_slug: str, index: int) -> Path | None:
    destination_dir = IMAGE_DIR / story_slug
    destination_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(destination_dir.glob(f"figure-{index:02d}.*"))
    if existing and existing[0].stat().st_size > 500:
        return existing[0]

    for attempt in range(5):
        try:
            response = session.get(url, timeout=45)
            response.raise_for_status()
            extension = extension_for(response.headers.get("content-type", ""), url)
            destination = destination_dir / f"figure-{index:02d}{extension}"
            temporary = destination.with_suffix(destination.suffix + ".part")
            temporary.write_bytes(response.content)
            if destination.suffix.lower() not in {".svg", ".gif"}:
                with Image.open(temporary) as image:
                    image.verify()
            temporary.replace(destination)
            return destination
        except Exception as exc:  # pragma: no cover - network failures are environmental
            if attempt == 4:
                print(f"warning: could not download {url}: {exc}")
                return None
            time.sleep(1.25 * (attempt + 1))
    return None


def story_summary(story: dict[str, Any]) -> str:
    return story.get("description") or story.get("subtitle") or "An essay by Aditya Singh."


def tag_chips(tags: list[str]) -> str:
    return "".join(f'<span class="topic-chip">{escape(tag)}</span>' for tag in tags)


def tracked_story_url(story: dict[str, Any], *, campaign: str = "evergreen_archive") -> str:
    base = f"{SITE_URL}articles/{story['slug']}/"
    return f"{base}?{urlencode({'utm_source': 'github_pages', 'utm_medium': 'referral', 'utm_campaign': campaign, 'utm_content': story['slug']})}"


def series_for_story(slug: str) -> list[dict[str, Any]]:
    return [series for series in SERIES if slug in series["stories"]]


def first_figure_alt(story: dict[str, Any]) -> str:
    for block in story.get("blocks", []):
        if block.get("type") == "figure" and block.get("alt"):
            return block["alt"]
    return f"Visual for {story['title']}"


def header(prefix: str = "") -> str:
    return f"""
<header class="site-header">
  <a class="brand" href="{prefix}index.html" aria-label="AS — Aditya Singh essays home">
    <span class="brand-mark">AS</span><span class="brand-name">Aditya Singh</span>
  </a>
  <nav class="site-nav" aria-label="Primary navigation">
    <a href="{prefix}index.html#stories">Stories</a>
    <a href="{prefix}series/">Series</a>
    <a href="{prefix}rss.xml">RSS</a>
    <a href="{MEDIUM_PROFILE}" target="_blank" rel="noopener noreferrer">Medium ↗</a>
    <button class="theme-toggle" type="button" aria-label="Switch color theme" data-theme-toggle>
      <span aria-hidden="true">◐</span>
    </button>
  </nav>
</header>"""


def footer(prefix: str = "") -> str:
    return f"""
<footer class="site-footer">
  <div><span class="brand-mark small">AS</span><p>Enterprise AI, agent architecture, and responsible systems.</p></div>
  <p>© <span data-year></span> {AUTHOR}. Independent essays, also available on <a href="{MEDIUM_PROFILE}" target="_blank" rel="noopener noreferrer">Medium</a>.</p>
</footer>"""


def document(
    *,
    title: str,
    description: str,
    canonical: str,
    body: str,
    prefix: str = "",
    image: str = "",
    article_meta: dict[str, str] | None = None,
    structured_data: list[dict[str, Any]] | None = None,
) -> str:
    image_meta = f'<meta property="og:image" content="{escape(image, quote=True)}">' if image else ""
    article_tags = ""
    if article_meta:
        article_tags = (
            '<meta property="og:type" content="article">'
            f'<meta property="article:published_time" content="{escape(article_meta.get("published", ""), quote=True)}">'
            f'<meta property="article:author" content="{escape(AUTHOR, quote=True)}">'
        )
    else:
        article_tags = '<meta property="og:type" content="website">'
    serialized_schema = [json.dumps(item, ensure_ascii=False).replace("</", "<\\/") for item in (structured_data or [])]
    json_ld = "\n".join(f'<script type="application/ld+json">{item}</script>' for item in serialized_schema)
    analytics_script_url = os.environ.get("SITE_ANALYTICS_SCRIPT_URL", "").strip()
    analytics_website_id = os.environ.get("SITE_ANALYTICS_WEBSITE_ID", "").strip()
    analytics = ""
    if analytics_script_url.startswith("https://") and analytics_website_id:
        analytics = (
            f'<script defer src="{escape(analytics_script_url, quote=True)}" '
            f'data-website-id="{escape(analytics_website_id, quote=True)}"></script>'
        )
    page = f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0d2425">
  <meta name="author" content="{AUTHOR}">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{escape(canonical, quote=True)}">
  {article_tags}
  {image_meta}
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{escape(canonical, quote=True)}">
  <link rel="alternate" type="application/atom+xml" title="Aditya Singh essays" href="{prefix}feed.xml">
  <link rel="alternate" type="application/rss+xml" title="Aditya Singh essays" href="{prefix}rss.xml">
  <link rel="alternate" type="application/feed+json" title="Aditya Singh essays" href="{prefix}feed.json">
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}assets/styles.css">
  {json_ld}
  {analytics}
  <script>try{{document.documentElement.dataset.theme=localStorage.getItem('as-theme')||'light'}}catch(e){{}}</script>
  <title>{escape(title)}</title>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="page-shell">
    {header(prefix)}
    {body}
    {footer(prefix)}
  </div>
  <script src="{prefix}assets/site.js" defer></script>
</body>
</html>
"""
    return "\n".join(line.rstrip() for line in page.splitlines()) + "\n"


def related_stories(story: dict[str, Any], stories: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    story_series = {item["slug"] for item in series_for_story(story["slug"])}
    story_tags = {tag.casefold() for tag in story.get("tags", [])}
    ranked: list[tuple[int, str, dict[str, Any]]] = []
    for candidate in stories:
        if candidate["slug"] == story["slug"]:
            continue
        candidate_series = {item["slug"] for item in series_for_story(candidate["slug"])}
        candidate_tags = {tag.casefold() for tag in candidate.get("tags", [])}
        score = 10 * len(story_series & candidate_series) + 2 * len(story_tags & candidate_tags)
        ranked.append((score, candidate.get("publishedAt", ""), candidate))
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [candidate for _, _, candidate in ranked[:limit]]


def render_article(story: dict[str, Any], stories: list[dict[str, Any]], session: requests.Session) -> None:
    slug = story["slug"]
    article_dir = ARTICLES_DIR / slug
    article_dir.mkdir(parents=True, exist_ok=True)
    used_ids: set[str] = set()
    toc: list[tuple[int, str, str]] = []
    rendered: list[str] = []
    figure_index = 0
    local_hero = ""
    page_url = f"{SITE_URL}articles/{slug}/"

    for block in story["blocks"]:
        if block["type"] == "figure":
            figure_index += 1
            source = block["src"]
            local_candidate = (ROOT / source).resolve() if not source.startswith(("http://", "https://")) else None
            if local_candidate and local_candidate.is_relative_to(ROOT) and local_candidate.exists():
                local = local_candidate
            else:
                local = download_image(session, source, slug, figure_index)
            src = f"../../{local.relative_to(ROOT).as_posix()}" if local else block["src"]
            if figure_index == 1 and local:
                local_hero = f"{SITE_URL}{local.relative_to(ROOT).as_posix()}"
            caption = block.get("caption", "")
            caption_html = f"<figcaption>{escape(caption)}</figcaption>" if caption else ""
            rendered.append(
                '<figure class="story-figure">'
                f'<img src="{escape(src, quote=True)}" alt="{escape(block.get("alt", ""), quote=True)}" loading="lazy" decoding="async">'
                f"{caption_html}</figure>"
            )
            continue

        tag = block.get("tag", "p")
        text = block.get("text", "").strip()
        inner = sanitize_inline(block.get("html", ""), story.get("canonical", MEDIUM_PROFILE))
        if not text and not inner:
            continue
        if tag in {"h2", "h3", "h4"}:
            level = 2 if tag == "h2" else 3
            anchor = heading_id(text, used_ids)
            toc.append((level, anchor, text))
            rendered.append(
                f'<h{level} id="{anchor}">{inner}<a class="heading-anchor" href="#{anchor}" aria-label="Link to {escape(text, quote=True)}">#</a></h{level}>'
            )
        elif tag == "blockquote":
            rendered.append(f"<blockquote>{inner}</blockquote>")
        elif tag == "pre":
            language = re.sub(r"[^a-z0-9_+-]", "", block.get("language", "").lower())
            class_attr = f' class="language-{language}"' if language else ""
            rendered.append(f"<pre><code{class_attr}>{escape(text)}</code></pre>")
        else:
            class_name = "disclosure" if text.lower().startswith("this story was written with") else ""
            class_attr = f' class="{class_name}"' if class_name else ""
            rendered.append(f"<p{class_attr}>{inner}</p>")

    toc_html = "".join(
        f'<li class="toc-level-{level}"><a href="#{anchor}">{escape(text)}</a></li>'
        for level, anchor, text in toc
    )
    current = stories.index(story)
    neighbors: list[str] = []
    if current > 0:
        newer = stories[current - 1]
        neighbors.append(
            f'<a class="story-nav-card" href="../{newer["slug"]}/"><span>Newer</span><strong>{escape(newer["title"])}</strong></a>'
        )
    if current + 1 < len(stories):
        older = stories[current + 1]
        neighbors.append(
            f'<a class="story-nav-card align-right" href="../{older["slug"]}/"><span>Older</span><strong>{escape(older["title"])}</strong></a>'
        )

    canonical_host = urlsplit(story["canonical"]).netloc.lower()
    if canonical_host.endswith("medium.com"):
        source_note = f"""
        <aside class="source-note">
          <span>Original publication</span>
          <p>This archive preserves the article as published. Read the canonical version on Medium for responses and updates.</p>
          <a href="{escape(story['canonical'], quote=True)}" target="_blank" rel="noopener noreferrer">Open on Medium ↗</a>
        </aside>"""
    else:
        source_note = f"""
        <aside class="source-note">
          <span>Canonical original</span>
          <p>This page is the original publication. Syndicated copies should retain this URL as their canonical source.</p>
          <a href="{escape(story['canonical'], quote=True)}">Canonical URL</a>
        </aside>"""

    related_cards = "".join(
        f'<a class="related-card" href="../{candidate["slug"]}/">'
        f'<span>{escape(" · ".join(candidate.get("tags", [])[:2]))}</span>'
        f'<strong>{escape(candidate["title"])}</strong>'
        f'<small>{escape(candidate.get("readTime", ""))}</small></a>'
        for candidate in related_stories(story, stories)
    )
    series_links = "".join(
        f'<a class="series-pill" href="../../series/{series["slug"]}/">{escape(series["title"])}</a>'
        for series in series_for_story(slug)
    )
    share_url = tracked_story_url(story)
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?{urlencode({'url': share_url})}"
    x_url = f"https://twitter.com/intent/tweet?{urlencode({'url': share_url, 'text': story['title']})}"
    email_url = f"mailto:?{urlencode({'subject': story['title'], 'body': share_url})}"
    engagement = f"""
  <section class="engagement-panel" aria-labelledby="continue-conversation">
    <div>
      <p class="eyebrow">Continue the conversation</p>
      <h2 id="continue-conversation">Share the architecture, or challenge it.</h2>
      <p>The links below include campaign parameters so referrals can be measured. Every share and discussion remains a human action.</p>
    </div>
    <div class="share-actions" aria-label="Share this story">
      <a href="{escape(linkedin_url, quote=True)}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
      <a href="{escape(x_url, quote=True)}" target="_blank" rel="noopener noreferrer">X</a>
      <a href="{escape(email_url, quote=True)}">Email</a>
      <button type="button" data-copy-url="{escape(share_url, quote=True)}">Copy tracked link</button>
      <a href="{DISCUSSIONS_URL}" target="_blank" rel="noopener noreferrer">Discuss on GitHub ↗</a>
    </div>
  </section>
  <section class="related-section" aria-labelledby="related-stories">
    <div class="related-heading"><div><p class="eyebrow">Read next</p><h2 id="related-stories">Related stories</h2></div><div class="series-links">{series_links}</div></div>
    <div class="related-grid">{related_cards}</div>
  </section>"""

    body = f"""
<div class="reading-progress" aria-hidden="true"><span data-progress></span></div>
<main id="main" class="article-page">
  <a class="back-link" href="../../index.html#stories">← All stories</a>
  <article>
    <header class="article-header">
      <div class="eyebrow">{date_label(story.get("publishedAt", ""))} <span>·</span> {escape(story.get("readTime", ""))}</div>
      <h1>{escape(story["title"])}</h1>
      <p class="article-deck">{escape(story.get("subtitle") or story_summary(story))}</p>
      <div class="article-byline">
        <span class="avatar">AS</span>
        <div><strong>{AUTHOR}</strong><span>Enterprise AI architect & writer</span></div>
      </div>
      <div class="topic-row">{tag_chips(story["tags"])}</div>
    </header>
    <div class="article-layout">
      <aside class="article-rail" aria-label="Table of contents">
        <p>In this essay</p><ol>{toc_html}</ol>
      </aside>
      <div class="article-body" data-article-body>
        {''.join(rendered)}
      </div>
    </div>
  </article>
  <div class="canonical-handoff">{source_note}</div>
  {engagement}
  <nav class="story-nav" aria-label="More stories">{''.join(neighbors)}</nav>
</main>"""

    schema: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": story["title"],
        "description": story_summary(story),
        "datePublished": story.get("publishedAt", ""),
        "dateModified": story.get("publishedAt", ""),
        "author": {"@type": "Person", "name": AUTHOR, "url": MEDIUM_PROFILE},
        "publisher": {"@type": "Person", "name": AUTHOR, "url": SITE_URL},
        "image": local_hero or story.get("heroImage", ""),
        "keywords": story.get("tags", []),
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "url": page_url,
    }
    if clean_url(story.get("canonical", "")) != page_url:
        schema["isBasedOn"] = clean_url(story["canonical"])
    page = document(
        title=f"{story['title']} — {AUTHOR}",
        description=story_summary(story),
        canonical=story["canonical"],
        body=body,
        prefix="../../",
        image=local_hero or story.get("heroImage", ""),
        article_meta={"published": story.get("publishedAt", "")},
        structured_data=[schema],
    )
    (article_dir / "index.html").write_text(page, encoding="utf-8")
    story["pageUrl"] = page_url
    story["localHero"] = local_hero
    story["heroAlt"] = first_figure_alt(story)


def render_index(stories: list[dict[str, Any]]) -> None:
    cards: list[str] = []
    for index, story in enumerate(stories):
        image_dir = IMAGE_DIR / story["slug"]
        local_candidates = sorted(image_dir.glob("figure-01.*"))
        image_src = local_candidates[0].relative_to(ROOT).as_posix() if local_candidates else story.get("heroImage", "")
        featured = " featured" if index == 0 else ""
        cards.append(f"""
<article class="story-card{featured}" data-story-card data-search="{escape((story['title'] + ' ' + story_summary(story) + ' ' + ' '.join(story['tags'])).lower(), quote=True)}">
  <a class="story-card-image" href="articles/{story['slug']}/" tabindex="-1" aria-hidden="true">
    <img src="{escape(image_src, quote=True)}" alt="{escape(story.get('heroAlt', ''), quote=True)}" loading="lazy" decoding="async">
  </a>
  <div class="story-card-copy">
    <div class="card-meta"><time datetime="{iso_date(story.get('publishedAt', ''))}">{date_label(story.get('publishedAt', ''))}</time><span>·</span><span>{escape(story.get('readTime', ''))}</span></div>
    <h2><a href="articles/{story['slug']}/">{escape(story['title'])}</a></h2>
    <p>{escape(story_summary(story))}</p>
    <div class="topic-row">{tag_chips(story['tags'])}</div>
    <a class="read-link" href="articles/{story['slug']}/">Read essay <span>→</span></a>
  </div>
</article>""")

    series_cards = "".join(
        f"""
<a class="series-card" href="series/{series['slug']}/">
  <span>{len(series['stories'])} {"story" if len(series['stories']) == 1 else "stories"}</span>
  <h3>{escape(series['title'])}</h3>
  <p>{escape(series['description'])}</p>
  <strong>Explore series →</strong>
</a>"""
        for series in SERIES
    )

    body = f"""
<main id="main">
  <section class="hero">
    <div class="hero-copy">
      <p class="eyebrow">Independent writing · Enterprise systems</p>
      <h1>Building AI systems that can act — <em>and be trusted.</em></h1>
      <p class="hero-intro">Essays on agent architecture, identity, economics, governance, and the operating models required to move enterprise AI from demo to production.</p>
      <div class="hero-actions">
        <a class="button primary" href="#stories">Explore the archive</a>
        <a class="button secondary" href="{MEDIUM_PROFILE}" target="_blank" rel="noopener noreferrer">Follow on Medium ↗</a>
      </div>
    </div>
    <aside class="hero-note">
      <span class="note-index">01 — {len(stories):02d}</span>
      <p>“The hard part of agentic AI is not making a model act. It is deciding what authority that action should carry.”</p>
      <span>Aditya Singh</span>
    </aside>
  </section>
  <section class="series-preview" aria-labelledby="series-heading">
    <div class="section-heading"><div><p class="eyebrow">Guided reading</p><h2 id="series-heading">Story series</h2></div><a class="section-link" href="series/">View all series →</a></div>
    <div class="series-grid">{series_cards}</div>
  </section>
  <section id="stories" class="stories-section">
    <div class="section-heading">
      <div><p class="eyebrow">The archive</p><h2>Published stories</h2></div>
      <label class="story-search"><span class="sr-only">Search stories</span><input type="search" placeholder="Search the archive" data-story-search><span aria-hidden="true">⌕</span></label>
    </div>
    <div class="stories-grid" data-story-grid>{''.join(cards)}</div>
    <p class="empty-state" data-empty-state hidden>No stories match that search.</p>
  </section>
  <section class="about-strip">
    <p class="eyebrow">About the author</p>
    <div><h2>Technology, operating models, and controls for consequential AI.</h2><p>Aditya Singh writes for leaders and builders translating agentic AI into production systems: architectures, economics, governance, and the decisions behind them.</p></div>
  </section>
</main>"""
    page = document(
        title=f"{AUTHOR} — Enterprise AI & Agent Architecture",
        description="Essays by Aditya Singh on enterprise AI, agent architecture, governance, identity, economics, and production systems.",
        canonical=SITE_URL,
        body=body,
        image=stories[0].get("localHero") or stories[0].get("heroImage", ""),
        structured_data=[{
            "@context": "https://schema.org",
            "@type": "Blog",
            "name": "Aditya Singh — Enterprise AI & Agent Architecture",
            "description": "Essays on enterprise AI, agent architecture, governance, identity, economics, and production systems.",
            "url": SITE_URL,
            "author": {"@type": "Person", "name": AUTHOR, "url": MEDIUM_PROFILE},
            "blogPost": [{"@type": "BlogPosting", "headline": story["title"], "url": story["pageUrl"]} for story in stories],
        }],
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")


def render_series(stories: list[dict[str, Any]]) -> None:
    series_root = ROOT / "series"
    series_root.mkdir(parents=True, exist_ok=True)
    by_slug = {story["slug"]: story for story in stories}
    overview_cards: list[str] = []

    for series in SERIES:
        members = [by_slug[slug] for slug in series["stories"] if slug in by_slug]
        overview_cards.append(f"""
<a class="series-card expanded" href="{series['slug']}/">
  <span>{len(members)} {"story" if len(members) == 1 else "stories"}</span>
  <h2>{escape(series['title'])}</h2>
  <p>{escape(series['description'])}</p>
  <ol>{''.join(f'<li>{escape(story["title"])}</li>' for story in members)}</ol>
  <strong>Read the series →</strong>
</a>""")

        member_cards = "".join(
            f"""
<article class="series-story">
  <span class="series-number">{index:02d}</span>
  <div><p class="card-meta">{date_label(story.get('publishedAt', ''))} · {escape(story.get('readTime', ''))}</p>
  <h2><a href="../../articles/{story['slug']}/">{escape(story['title'])}</a></h2>
  <p>{escape(story_summary(story))}</p>
  <a class="read-link" href="../../articles/{story['slug']}/">Read essay <span>→</span></a></div>
</article>"""
            for index, story in enumerate(members, 1)
        )
        detail_url = f"{SITE_URL}series/{series['slug']}/"
        detail_body = f"""
<main id="main" class="series-page">
  <a class="back-link" href="../">← All series</a>
  <header class="series-hero"><p class="eyebrow">Reading series · {len(members)} {"story" if len(members) == 1 else "stories"}</p><h1>{escape(series['title'])}</h1><p>{escape(series['description'])}</p></header>
  <section class="series-story-list" aria-label="Stories in reading order">{member_cards}</section>
</main>"""
        detail_schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": series["title"],
            "description": series["description"],
            "url": detail_url,
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {"@type": "ListItem", "position": index, "url": story["pageUrl"], "name": story["title"]}
                    for index, story in enumerate(members, 1)
                ],
            },
        }
        detail_dir = series_root / series["slug"]
        detail_dir.mkdir(parents=True, exist_ok=True)
        (detail_dir / "index.html").write_text(
            document(
                title=f"{series['title']} — {AUTHOR}",
                description=series["description"],
                canonical=detail_url,
                body=detail_body,
                prefix="../../",
                image=members[0].get("localHero", "") if members else "",
                structured_data=[detail_schema],
            ),
            encoding="utf-8",
        )

    overview_body = f"""
<main id="main" class="series-page">
  <header class="series-hero"><p class="eyebrow">Guided reading</p><h1>Story series</h1><p>Follow the architecture from foundational controls to production operating models. Each sequence is arranged as a deliberate reading path.</p></header>
  <section class="series-grid overview" aria-label="Available story series">{''.join(overview_cards)}</section>
</main>"""
    overview_url = f"{SITE_URL}series/"
    (series_root / "index.html").write_text(
        document(
            title=f"Story Series — {AUTHOR}",
            description="Guided reading paths through Aditya Singh's essays on production AI agents, agentic CRM, and AI economics.",
            canonical=overview_url,
            body=overview_body,
            prefix="../",
            structured_data=[{
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": "Story series",
                "url": overview_url,
                "hasPart": [{"@type": "CollectionPage", "name": item["title"], "url": f"{overview_url}{item['slug']}/"} for item in SERIES],
            }],
        ),
        encoding="utf-8",
    )


def render_supporting_files(stories: list[dict[str, Any]]) -> None:
    series_urls = [f"{SITE_URL}series/", *[f"{SITE_URL}series/{series['slug']}/" for series in SERIES]]
    sitemap_urls = [SITE_URL, *series_urls, *[f"{SITE_URL}articles/{story['slug']}/" for story in stories]]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sitemap_urls:
        sitemap.append(f"  <url><loc>{escape(url)}</loc></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")

    updated = stories[0].get("publishedAt") or datetime.now(timezone.utc).isoformat()
    atom_entries = []
    rss_items = []
    json_items = []
    for story in stories:
        page_url = story["pageUrl"]
        summary = story_summary(story)
        published = story.get("publishedAt", "")
        published_dt = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else datetime.now(timezone.utc)
        atom_entries.append(
            "  <entry>"
            f"<title>{escape(story['title'])}</title>"
            f"<link href=\"{escape(page_url, quote=True)}\"/>"
            f"<id>{escape(page_url)}</id><published>{escape(published)}</published><updated>{escape(published)}</updated>"
            f"<summary>{escape(summary)}</summary></entry>"
        )
        rss_items.append(
            "    <item>"
            f"<title>{escape(story['title'])}</title><link>{escape(page_url)}</link><guid>{escape(page_url)}</guid>"
            f"<pubDate>{format_datetime(published_dt)}</pubDate><description>{escape(summary)}</description></item>"
        )
        json_items.append({
            "id": page_url,
            "url": page_url,
            "external_url": clean_url(story.get("canonical", "")),
            "title": story["title"],
            "summary": summary,
            "date_published": published,
            "tags": story.get("tags", []),
        })

    atom = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f"  <title>Aditya Singh essays</title><id>{SITE_URL}</id><link href=\"{SITE_URL}feed.xml\" rel=\"self\"/>"
        f"<link href=\"{SITE_URL}\"/><updated>{escape(updated)}</updated><author><name>{AUTHOR}</name></author>\n"
        + "\n".join(atom_entries)
        + "\n</feed>\n"
    )
    (ROOT / "feed.xml").write_text(atom, encoding="utf-8")
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
        f"<title>Aditya Singh essays</title><link>{SITE_URL}</link><description>Enterprise AI and agent architecture essays.</description>\n"
        + "\n".join(rss_items)
        + "\n</channel></rss>\n"
    )
    (ROOT / "rss.xml").write_text(rss, encoding="utf-8")
    json_feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Aditya Singh essays",
        "home_page_url": SITE_URL,
        "feed_url": f"{SITE_URL}feed.json",
        "authors": [{"name": AUTHOR, "url": MEDIUM_PROFILE}],
        "items": json_items,
    }
    (ROOT / "feed.json").write_text(json.dumps(json_feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = [
        {
            "slug": story["slug"],
            "title": story["title"],
            "description": story_summary(story),
            "publishedAt": story.get("publishedAt", ""),
            "readTime": story.get("readTime", ""),
            "tags": story["tags"],
            "canonical": story["canonical"],
            "pageUrl": f"{SITE_URL}articles/{story['slug']}/",
            "trackedUrl": tracked_story_url(story),
            "series": [series["slug"] for series in series_for_story(story["slug"])],
        }
        for story in stories
    ]
    (DATA_DIR / "stories.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    stories = load_stories()
    if not stories:
        raise SystemExit("No story snapshots found in data/.")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; MediumArchiveBuilder/1.0)"})
    for story in stories:
        print(f"building: {story['title']}")
        render_article(story, stories, session)
    render_index(stories)
    render_series(stories)
    render_supporting_files(stories)
    digest = hashlib.sha256("".join(story["id"] for story in stories).encode()).hexdigest()[:12]
    print(f"built {len(stories)} stories ({digest})")


if __name__ == "__main__":
    main()
