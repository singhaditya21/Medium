#!/usr/bin/env python3
"""Build a static GitHub Pages archive from the Medium story snapshots in data/."""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
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

TOPIC_MAP = {
    "ai-agent-identity-is-not-enough": ["AI agents", "Authorization", "Cybersecurity"],
    "what-an-agent-actually-costs": ["AI economics", "FinOps", "Enterprise AI"],
    "enterprise-agent-control-tower": ["Agent governance", "Architecture", "Risk"],
    "agentic-crm-reference-architecture": ["Agentic CRM", "Architecture", "Enterprise AI"],
    "traditional-crm-agentic-ai": ["Agentic CRM", "Strategy", "Transformation"],
}

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


def header(prefix: str = "") -> str:
    return f"""
<header class="site-header">
  <a class="brand" href="{prefix}index.html" aria-label="Aditya Singh essays home">
    <span class="brand-mark">AS</span><span class="brand-name">Aditya Singh</span>
  </a>
  <nav class="site-nav" aria-label="Primary navigation">
    <a href="{prefix}index.html#stories">Stories</a>
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
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}assets/styles.css">
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


def render_article(story: dict[str, Any], stories: list[dict[str, Any]], session: requests.Session) -> None:
    slug = story["slug"]
    article_dir = ARTICLES_DIR / slug
    article_dir.mkdir(parents=True, exist_ok=True)
    used_ids: set[str] = set()
    toc: list[tuple[int, str, str]] = []
    rendered: list[str] = []
    figure_index = 0
    local_hero = ""

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
            rendered.append(f"<pre><code>{escape(text)}</code></pre>")
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
  <nav class="story-nav" aria-label="More stories">{''.join(neighbors)}</nav>
</main>"""

    page_url = f"{SITE_URL}articles/{slug}/"
    page = document(
        title=f"{story['title']} — {AUTHOR}",
        description=story_summary(story),
        canonical=story["canonical"],
        body=body,
        prefix="../../",
        image=local_hero or story.get("heroImage", ""),
        article_meta={"published": story.get("publishedAt", "")},
    )
    (article_dir / "index.html").write_text(page, encoding="utf-8")
    story["pageUrl"] = page_url
    story["localHero"] = local_hero


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
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")


def render_supporting_files(stories: list[dict[str, Any]]) -> None:
    sitemap_urls = [SITE_URL] + [f"{SITE_URL}articles/{story['slug']}/" for story in stories]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sitemap_urls:
        sitemap.append(f"  <url><loc>{escape(url)}</loc></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
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
    render_supporting_files(stories)
    digest = hashlib.sha256("".join(story["id"] for story in stories).encode()).hexdigest()[:12]
    print(f"built {len(stories)} stories ({digest})")


if __name__ == "__main__":
    main()
