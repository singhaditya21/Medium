#!/usr/bin/env python3
"""Create a deterministic weekly editorial brief without taking public actions."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from build_site import ROOT, load_stories, story_summary, tracked_story_url


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "editorial-brief")
    args = parser.parse_args()
    stories = load_stories()
    year, week, _ = date.today().isocalendar()
    story = stories[(week - 1) % len(stories)]
    story["pageUrl"] = f"https://singhaditya21.github.io/Medium/articles/{story['slug']}/"
    title = f"Editorial brief · {year}-W{week:02d} · {story['title']}"
    body = f"""## This week's flagship

**{story['title']}**

{story_summary(story)}

Tracked URL: {tracked_story_url(story, campaign=f'weekly_{year}_w{week:02d}')}

## Editorial plan

- [ ] Re-read the story and verify time-sensitive claims and source links.
- [ ] Select one diagram and one technical claim for a visual excerpt.
- [ ] Edit the generated distribution pack into your own final wording.
- [ ] Publish or resurface on one primary channel; avoid posting identical text everywhere at once.
- [ ] Invite one specific technical question rather than asking for generic engagement.
- [ ] Respond manually to substantive comments and record recurring questions.
- [ ] If appropriate, research and submit to one relevant Medium publication manually.
- [ ] Record presentations, views, reads, followers, subscribers, and referrers after seven days.

## Guardrails

- No automated claps, follows, highlights, responses, reposts, views, or publication submissions.
- No Medium cookies or signed-in session data in GitHub Actions.
- Do not invent first-person experience, customer evidence, or implementation results.
- Review AI-assistance disclosure and paywall eligibility in Medium before publication.
"""
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "title.txt").write_text(title + "\n", encoding="utf-8")
    (args.output_dir / "body.md").write_text(body, encoding="utf-8")
    print(title)


if __name__ == "__main__":
    main()
