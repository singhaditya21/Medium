#!/usr/bin/env python3
"""Build a policy-aware handoff for importing one GitHub story into a Medium draft."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from build_site import ROOT, SITE_URL, first_figure_alt, load_stories, story_summary


CONFIG_DIR = ROOT / "medium" / "releases"
PUBLICATION_REGISTRY_PATH = ROOT / "medium" / "publications.json"
EXECUTIONS_DIR = ROOT / "medium" / "executions"
DEFAULT_OUTPUT_DIR = ROOT / "medium-release-bundles"
POLICY_REFERENCES = {
    "api": "https://help.medium.com/hc/en-us/articles/213480228-API-Importing",
    "import": "https://help.medium.com/hc/en-us/articles/214550207-Importing-a-post-to-Medium",
    "canonical": "https://help.medium.com/hc/en-us/articles/360033930293-Set-a-canonical-link",
    "rules": "https://help.medium.com/hc/en-us/articles/213477928-Medium-Rules",
    "ai": "https://help.medium.com/hc/en-us/articles/22576852947223-Artificial-Intelligence-AI-content-policy",
}
DISCLOSURE_MARKERS = ("ai writing", "ai-generated", "ai generated", "artificial intelligence", "with ai assistance")


def source_url(story: dict[str, Any]) -> str:
    return f"{SITE_URL}articles/{story['slug']}/"


def text_blocks(story: dict[str, Any]) -> list[str]:
    return [
        block.get("text", "").strip()
        for block in story.get("blocks", [])
        if block.get("type") != "figure" and block.get("text", "").strip()
    ]


def disclosure_check(story: dict[str, Any]) -> tuple[bool, str, int | None]:
    for index, text in enumerate(text_blocks(story)[:2], 1):
        lowered = text.casefold()
        if any(marker in lowered for marker in DISCLOSURE_MARKERS):
            return True, text, index
    return False, "", None


def figure_checks(story: dict[str, Any]) -> dict[str, Any]:
    figures = [block for block in story.get("blocks", []) if block.get("type") == "figure"]
    return {
        "count": len(figures),
        "allHaveAltText": all(block.get("alt", "").strip() for block in figures),
        "allHaveCaptions": all(block.get("caption", "").strip() for block in figures),
        "aiAssistanceLabeledCount": sum("ai-assisted" in block.get("caption", "").casefold() for block in figures),
    }


def load_publication_registry(stories: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Load the reviewed Medium publication state used for duplicate prevention."""
    try:
        document = json.loads(PUBLICATION_REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing publication registry: {PUBLICATION_REGISTRY_PATH.relative_to(ROOT)}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid publication registry JSON: {exc}") from exc

    if document.get("schemaVersion") != 1:
        raise ValueError("publication registry schemaVersion must be 1")
    records = document.get("stories")
    if not isinstance(records, list):
        raise ValueError("publication registry stories must be an array")

    expected_slugs = {story["slug"] for story in stories}
    registry: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            errors.append("every publication registry entry must be an object")
            continue
        slug = record.get("storySlug")
        status = record.get("status")
        medium_url = record.get("mediumUrl")
        if not isinstance(slug, str) or not slug:
            errors.append("every publication registry entry needs a storySlug")
            continue
        if slug in registry:
            errors.append(f"duplicate publication registry entry: {slug}")
            continue
        if slug not in expected_slugs:
            errors.append(f"unknown story in publication registry: {slug}")
        if status not in {"published", "not_published"}:
            errors.append(f"{slug}: status must be published or not_published")
        if status == "published":
            if not isinstance(medium_url, str) or not urlsplit(medium_url).netloc.casefold().endswith("medium.com"):
                errors.append(f"{slug}: published stories need a medium.com mediumUrl")
        elif medium_url is not None:
            errors.append(f"{slug}: a not_published story must have a null mediumUrl")
        registry[slug] = record

    missing = expected_slugs - set(registry)
    errors.extend(f"missing publication registry entry: {slug}" for slug in sorted(missing))
    stories_by_slug = {story["slug"]: story for story in stories}
    for slug, record in registry.items():
        story = stories_by_slug.get(slug)
        if not story:
            continue
        canonical_host = urlsplit(story.get("canonical", "")).netloc.casefold()
        if canonical_host.endswith("medium.com") and record.get("status") != "published":
            errors.append(f"{slug}: a Medium canonical conflicts with not_published registry status")
    if errors:
        raise ValueError("; ".join(errors))
    return registry


def load_signed_in_story_states() -> dict[str, str]:
    """Return the latest verified signed-in state without exposing private draft URLs."""
    states: dict[str, tuple[str, str]] = {}
    for path in sorted(EXECUTIONS_DIR.glob("*.json")):
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        action = receipt.get("action")
        result = receipt.get("result", {})
        story_slug = result.get("storySlug")
        recorded_at = receipt.get("recordedAt", "")
        if not isinstance(story_slug, str):
            continue
        if action == "draft_imported" and result.get("status") == "draft_saved":
            state = "draft_saved"
        elif action == "story_published" and result.get("status") == "published":
            state = "published"
        else:
            continue
        if story_slug not in states or recorded_at > states[story_slug][0]:
            states[story_slug] = (recorded_at, state)
    return {slug: state for slug, (_, state) in states.items()}


def load_config(story: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    path = CONFIG_DIR / f"{story['slug']}.json"
    if not path.exists():
        return None, [f"missing release configuration: {path.relative_to(ROOT)}"]
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"invalid release configuration JSON: {exc}"]
    errors: list[str] = []
    expected_url = source_url(story)
    if config.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    if config.get("storySlug") != story["slug"]:
        errors.append("storySlug does not match the source story")
    if config.get("operation") != "import_to_private_draft":
        errors.append("operation must be import_to_private_draft")
    topics = config.get("topics")
    if not isinstance(topics, list) or not 1 <= len(topics) <= 5 or not all(isinstance(item, str) and item.strip() for item in topics):
        errors.append("topics must contain one to five non-empty strings")
    elif len(set(topics)) != len(topics):
        errors.append("topics must not contain duplicates")
    if config.get("canonicalUrl") != expected_url:
        errors.append(f"canonicalUrl must equal {expected_url}")
    if config.get("subscriberEmail") is not False:
        errors.append("subscriberEmail must remain false during draft preparation")
    if config.get("paywall") is not False:
        errors.append("paywall must remain false during draft preparation")
    if config.get("allowUnattendedPublish") is not False:
        errors.append("allowUnattendedPublish must be false")
    if config.get("requiresFinalConfirmation") is not True:
        errors.append("requiresFinalConfirmation must be true")
    if config.get("humanReviewRequired") is not True:
        errors.append("humanReviewRequired must be true")
    if config.get("scheduleAt") is not None:
        errors.append("scheduleAt must remain null until final confirmation")
    publication = config.get("publication")
    if publication is not None and not isinstance(publication, str):
        errors.append("publication must be null or a publication name")
    return config, errors


def build_bundle(
    story: dict[str, Any],
    publication_record: dict[str, Any],
    signed_in_state: str | None,
) -> tuple[dict[str, Any], list[str]]:
    canonical_host = urlsplit(story.get("canonical", "")).netloc.casefold()
    canonical_on_medium = canonical_host.endswith("medium.com")
    registry_on_medium = publication_record["status"] == "published"
    already_on_medium = canonical_on_medium or registry_on_medium
    existing_medium_draft = signed_in_state == "draft_saved" and not already_on_medium
    existing_medium_url = publication_record.get("mediumUrl")
    if not existing_medium_url and canonical_on_medium:
        existing_medium_url = story.get("canonical")
    if already_on_medium:
        config, config_errors = None, []
    else:
        config, config_errors = load_config(story)
    disclosure_found, disclosure_text, disclosure_paragraph = disclosure_check(story)
    figures = figure_checks(story)
    page_path = ROOT / "articles" / story["slug"] / "index.html"
    issues = list(config_errors)
    if already_on_medium:
        issues.append("story is already recorded as published on Medium; importing it again would create a duplicate")
    elif existing_medium_draft:
        issues.append("story already has a verified saved Medium draft; importing it again would create a duplicate draft")
    if not page_path.exists():
        issues.append("generated GitHub Pages story is missing")
    if not disclosure_found:
        issues.append("AI-assistance disclosure was not found within the first two text paragraphs")
    if not figures["allHaveAltText"] or not figures["allHaveCaptions"]:
        issues.append("all figures must have alt text and captions before Medium transfer")

    status = "blocked"
    if already_on_medium:
        status = "blocked_existing_medium_story"
    elif existing_medium_draft:
        status = "blocked_existing_medium_draft"
    elif not issues:
        status = "ready_for_private_draft_import"

    settings = config or {
        "operation": "import_to_private_draft",
        "topics": story.get("tags", [])[:5],
        "canonicalUrl": source_url(story),
        "publication": None,
        "subscriberEmail": False,
        "paywall": False,
        "scheduleAt": None,
        "allowUnattendedPublish": False,
        "requiresFinalConfirmation": True,
        "humanReviewRequired": True,
    }
    bundle = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "story": {
            "slug": story["slug"],
            "title": story["title"],
            "author": story.get("author", "Aditya Singh"),
            "description": story_summary(story),
            "sourceUrl": source_url(story),
            "sourceCanonical": story.get("canonical", ""),
            "existingMediumUrl": existing_medium_url,
            "heroDescription": first_figure_alt(story),
        },
        "medium": {
            "operation": settings.get("operation"),
            "targetState": "private_draft",
            "topics": settings.get("topics", []),
            "canonicalUrl": settings.get("canonicalUrl"),
            "publication": settings.get("publication"),
            "subscriberEmail": settings.get("subscriberEmail"),
            "paywall": settings.get("paywall"),
            "scheduleAt": settings.get("scheduleAt"),
            "publish": False,
        },
        "contentChecks": {
            "disclosureFound": disclosure_found,
            "disclosureParagraph": disclosure_paragraph,
            "disclosureText": disclosure_text,
            "figureCount": figures["count"],
            "allFiguresHaveAltText": figures["allHaveAltText"],
            "allFiguresHaveCaptions": figures["allHaveCaptions"],
            "aiAssistanceLabeledFigureCount": figures["aiAssistanceLabeledCount"],
            "generatedPageExists": page_path.exists(),
            "alreadyPublishedOnMedium": already_on_medium,
            "existingSavedMediumDraft": existing_medium_draft,
            "publicationRegistryStatus": publication_record["status"],
        },
        "approvalGates": {
            "draftImportRequiresExplicitRequest": True,
            "publishRequiresActionTimeConfirmation": True,
            "finalSettingsMustBeReconfirmed": ["topics", "publication", "schedule", "subscriber email", "paywall", "canonical URL"],
            "allowUnattendedPublish": False,
        },
        "verification": {
            "expectedTitle": story["title"],
            "expectedFigureCount": figures["count"],
            "expectedDisclosureWithinFirstTwoParagraphs": True,
            "expectedCanonicalUrl": source_url(story),
            "expectedFinalState": "DraftSaved",
        },
        "issues": issues,
        "policyReferences": POLICY_REFERENCES,
    }
    return bundle, issues


def markdown_summary(bundle: dict[str, Any]) -> str:
    story = bundle["story"]
    medium = bundle["medium"]
    checks = bundle["contentChecks"]
    issues = bundle["issues"]
    issue_lines = "\n".join(f"- {item}" for item in issues) if issues else "- None"
    topics = ", ".join(medium["topics"]) or "Not configured"
    return f"""# Medium release: {story['title']}

Status: **{bundle['status']}**

This is an approval-gated release handoff. GitHub Actions does not sign in to Medium and does not publish the story.

## Exact draft-import target

- Source URL: {story['sourceUrl']}
- Target state: private Medium draft
- Topics prepared: {topics}
- Publication: {medium['publication'] or 'Profile / not selected'}
- Subscriber email: disabled
- Paywall: disabled
- Schedule: not set
- Canonical URL: {medium['canonicalUrl']}
- Publish during import: **no**

## Content checks

- AI disclosure in first two paragraphs: {checks['disclosureFound']}
- Figures: {checks['figureCount']}
- All figures have alt text: {checks['allFiguresHaveAltText']}
- All figures have captions: {checks['allFiguresHaveCaptions']}
- Figures explicitly labeled AI-assisted: {checks['aiAssistanceLabeledFigureCount']}
- Existing Medium publication detected: {checks['alreadyPublishedOnMedium']}
- Existing saved Medium draft detected: {checks['existingSavedMediumDraft']}
- Existing Medium URL: {story['existingMediumUrl'] or 'None'}
- Publication registry status: {checks['publicationRegistryStatus']}

## Blocking issues

{issue_lines}

## Required execution sequence

1. Review this bundle and explicitly request import of this exact story into a private Medium draft.
2. Use the signed-in Medium UI to import the GitHub Pages URL; do not use account cookies in GitHub.
3. Verify title, disclosure, headings, code, figures, captions, alt text, links, and canonical URL.
4. Leave the result as `DraftSaved`.
5. Separately confirm topics, publication, schedule, subscriber email, paywall, and canonical URL immediately before any Publish or Schedule action.

## Integrity boundary

- No unattended or programmatic Medium publishing.
- No automated claps, follows, highlights, responses, reposts, or traffic.
- No invented personal experience, customer evidence, results, or claims.
- No duplicate import when the source story is already published on Medium.
"""


def write_bundle(bundle: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    destination = output_dir / bundle["story"]["slug"]
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "release.json"
    markdown_path = destination / "release.md"
    json_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown_summary(bundle), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--slug")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--strict", action="store_true", help="fail when an eligible GitHub-original story has a blocking issue")
    args = parser.parse_args()
    stories = load_stories()
    signed_in_story_states = load_signed_in_story_states()
    try:
        publication_registry = load_publication_registry(stories)
    except ValueError as exc:
        raise SystemExit(f"Medium publication registry validation failed: {exc}") from exc
    if args.slug:
        stories = [story for story in stories if story["slug"] == args.slug]
        if not stories:
            raise SystemExit(f"Unknown story slug: {args.slug}")

    failures: list[str] = []
    for story in stories:
        bundle, issues = build_bundle(
            story,
            publication_registry[story["slug"]],
            signed_in_story_states.get(story["slug"]),
        )
        json_path, _ = write_bundle(bundle, args.output_dir)
        print(f"{bundle['status']}: {json_path}")
        eligible_for_import = not (
            bundle["contentChecks"]["alreadyPublishedOnMedium"]
            or bundle["contentChecks"]["existingSavedMediumDraft"]
        )
        if args.strict and eligible_for_import and issues:
            failures.append(f"{story['slug']}: {'; '.join(issues)}")
        if args.slug and bundle["status"].startswith("blocked"):
            failures.append(f"{story['slug']}: {'; '.join(issues)}")
    if failures:
        print("Medium release preparation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
