#!/usr/bin/env python3
"""Generate human-review distribution assets for one or more stories."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from build_site import ROOT, first_figure_alt, load_stories, series_for_story, story_summary, tracked_story_url


def pack(story: dict, output_dir: Path) -> Path:
    campaign = f"distribution_{datetime.now(timezone.utc):%Y_%m}"
    url = tracked_story_url(story, campaign=campaign)
    tags = story.get("tags", [])[:5]
    series = [item["title"] for item in series_for_story(story["slug"])]
    summary = story_summary(story)
    title = story["title"]
    lines = [
        f"# Distribution pack: {title}",
        "",
        "> Draft assets only. Review every claim and edit for your own voice before any public action.",
        "",
        "## Source links",
        "",
        f"- GitHub Pages: {story['pageUrl']}",
        f"- Tracked campaign URL: {url}",
        f"- Canonical URL: {story['canonical']}",
        f"- Series: {', '.join(series) or 'Standalone'}",
        f"- Lead visual description: {first_figure_alt(story)}",
        "",
        "## Medium import checklist",
        "",
        "- [ ] Import from the GitHub Pages URL; do not paste a duplicate without checking the canonical URL.",
        "- [ ] Confirm title, subtitle, headings, code, formulas, captions, and all figure order after import.",
        "- [ ] Add an accurate AI-assistance disclosure where Medium policy requires it.",
        "- [ ] Confirm paywall eligibility and distribution settings in Medium before publishing.",
        f"- [ ] Select up to five topics: {', '.join(tags)}.",
        "- [ ] Preview desktop and mobile rendering.",
        "",
        "## Publication submission checklist",
        "",
        "- [ ] Identify one relevant active publication and read its current submission rules.",
        "- [ ] Verify the publication accepts previously published or imported work.",
        "- [ ] Tailor the pitch to the publication's readers; do not send a generic bulk pitch.",
        "- [ ] Submit manually from the signed-in Medium story menu.",
        "- [ ] Record the publication, submission date, and result in the editorial issue.",
        "",
        "## LinkedIn draft",
        "",
        f"**Architecture question:** {title}",
        "",
        summary,
        "",
        "The useful debate is not whether an agent can complete the task. It is which evidence, authority, verification, and recovery conditions must be true before the action is allowed.",
        "",
        f"Read the full technical breakdown: {url}",
        "",
        f"{' '.join('#' + tag.replace(' ', '') for tag in tags[:4])}",
        "",
        "## X draft",
        "",
        f"{title}\n\n{summary}\n\n{url}",
        "",
        "## Email/newsletter draft",
        "",
        f"**Subject:** {title}",
        "",
        f"{summary}\n\nThis piece includes the architecture, control boundaries, and implementation details. Read it here: {url}",
        "",
        "## Conversation prompts",
        "",
        "1. Which control would be hardest to implement in your current architecture?",
        "2. Where should the system fail closed, and where is graceful degradation safer?",
        "3. What evidence would you require before reducing human approval?",
        "",
        "## Manual release gate",
        "",
        "- [ ] I reviewed the drafts and removed any claim I cannot support.",
        "- [ ] I confirmed no personal experience, customer result, or field observation was invented.",
        "- [ ] I confirmed disclosure, canonical, and publication requirements.",
        "- [ ] I will perform each post, submission, or reply myself from the relevant account.",
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{story['slug']}.md"
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--slug")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "distribution-packs")
    args = parser.parse_args()
    stories = load_stories()
    if args.slug:
        stories = [story for story in stories if story["slug"] == args.slug]
        if not stories:
            raise SystemExit(f"Unknown story slug: {args.slug}")
    elif not args.all:
        stories = stories[:1]
    for story in stories:
        story["pageUrl"] = f"https://singhaditya21.github.io/Medium/articles/{story['slug']}/"
        print(pack(story, args.output_dir))


if __name__ == "__main__":
    main()
