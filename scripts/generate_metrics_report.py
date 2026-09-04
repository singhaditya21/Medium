#!/usr/bin/env python3
"""Build the canonical all-story Medium performance scorecard."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from build_site import ROOT


BASELINE = ROOT / "analytics" / "engagement-baseline.json"
SNAPSHOTS_DIR = ROOT / "analytics" / "snapshots"
INVENTORY = ROOT / "analytics" / "medium-content-inventory-2026-09-03.json"
ARTIFACT = ROOT / "analytics" / "engagement-dashboard.artifact.json"

SEVEN_DAY_FLOOR = {"presentations": 5, "views": 3, "reads": 1}
RETENTION_SAMPLE_FLOOR = 20


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).strip()


def parse_published_date(label: str) -> date:
    return datetime.strptime(label, "%d %b %Y").date()


def friendly_datetime(value: datetime) -> str:
    month = value.strftime("%b")
    hour = value.strftime("%I").lstrip("0") or "0"
    return f"{month} {value.day}, {value.year} · {hour}:{value.strftime('%M %p')} IST"


def evidence_maturity(views: int) -> str:
    if views < 5:
        return "Nascent (<5 views)"
    if views < RETENTION_SAMPLE_FLOOR:
        return "Early (5–19 views)"
    return "Decision-ready (20+ views)"


def classify_story(age_days: int, presentations: int, views: int, reads: int, read_ratio: float) -> tuple[str, str, str]:
    if age_days < 2:
        return "Monitor · <48h", "P2", "Capture the 48-hour checkpoint; make no packaging or body change yet."
    if age_days < 7:
        return "Monitor · pre-7d", "P2", "Capture the seven-day checkpoint before diagnosing the story."
    if presentations < SEVEN_DAY_FLOOR["presentations"]:
        return "Distribution priority", "P1", "Audit topics, visibility and publication fit before changing the story body."
    if views < SEVEN_DAY_FLOOR["views"]:
        return "Packaging priority", "P1", "Test the title, subtitle and hero because presentations exist but opens do not."
    if reads == 0 and views < RETENTION_SAMPLE_FLOOR:
        return "Retention signal · low sample", "P1", "Inspect traffic and the first screen; wait for 20 views before a structural rewrite."
    if views >= RETENTION_SAMPLE_FLOOR and read_ratio < 0.20:
        return "Retention priority", "P1", "Tighten the opening and accelerate time-to-value."
    if read_ratio >= 0.50:
        return "Strong baseline", "P3", "Reuse the structure and internal-navigation pattern in the next related story."
    if read_ratio >= 0.20:
        return "Working baseline", "P3", "Preserve the body and continue qualified distribution."
    return "Retention watch", "P2", "Monitor to 20 views, then test the opening if the ratio remains below 20%."


def checkpoint_status(age_days: int, presentations: int, views: int, reads: int) -> str:
    if age_days < 7:
        return "Not due"
    passed = (
        presentations >= SEVEN_DAY_FLOOR["presentations"]
        and views >= SEVEN_DAY_FLOOR["views"]
        and reads >= SEVEN_DAY_FLOOR["reads"]
    )
    return "Pass" if passed else "Miss"


def source_objects(captured_at: str, current_path: str, previous_path: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "scorecard_summary",
            "label": "Medium portfolio scorecard summary",
            "path": current_path,
            "query": {
                "engine": "sqlite",
                "language": "sql",
                "sql": f"""WITH current_doc(doc) AS (
  SELECT CAST(readfile('{current_path}') AS TEXT)
), previous_doc(doc) AS (
  SELECT CAST(readfile('{previous_path}') AS TEXT)
), story AS (
  SELECT json_extract(value, '$.slug') AS slug,
         json_extract(value, '$.presentations') AS presentations,
         json_extract(value, '$.views') AS views,
         json_extract(value, '$.reads') AS reads
  FROM current_doc, json_each(current_doc.doc, '$.scopes.storyLifetime')
), prior AS (
  SELECT json_extract(value, '$.slug') AS slug,
         json_extract(value, '$.reads') AS reads
  FROM previous_doc, json_each(previous_doc.doc, '$.scopes.storyLifetime')
)
SELECT COUNT(*) AS published_stories,
       SUM(presentations) AS lifetime_presentations,
       SUM(views) AS lifetime_views,
       SUM(reads) AS lifetime_reads,
       SUM(reads) * 1.0 / NULLIF(SUM(views), 0) AS portfolio_read_ratio,
       SUM(CASE WHEN reads > 0 THEN 1 ELSE 0 END) AS stories_with_reads,
       SUM(CASE WHEN slug NOT IN ('model-routing-is-capital-allocation', 'your-multi-agent-system-is-a-distributed-system') THEN 1 ELSE 0 END) AS eligible_7d_stories,
       SUM(CASE WHEN slug NOT IN ('model-routing-is-capital-allocation', 'your-multi-agent-system-is-a-distributed-system') AND presentations >= 5 AND views >= 3 AND reads >= 1 THEN 1 ELSE 0 END) AS checkpoint_7d_passes,
       (SELECT SUM(story.reads) FROM story JOIN prior USING (slug)) - (SELECT SUM(reads) FROM prior) AS delta_common_reads_vs_previous
FROM story""",
                "description": "Portfolio totals and the account-specific seven-day checkpoint calculated from the latest signed-in story snapshot.",
                "executed_at": captured_at,
                "tables_used": [current_path, previous_path],
                "filters": ["Account: @singhaditya21_89007", "Published Medium stories", "Seven-day eligibility as of September 4, 2026"],
                "metric_definitions": [
                    "Portfolio read ratio = sum of lifetime reads divided by sum of lifetime views across published stories.",
                    "Seven-day checkpoint pass = at least 5 presentations, 3 views, and 1 read for a story published at least 7 calendar days before capture."
                ]
            }
        },
        {
            "id": "scorecard_inputs",
            "label": "Medium story scorecard inputs",
            "path": current_path,
            "query": {
                "engine": "sqlite",
                "language": "sql",
                "sql": f"""WITH current_doc(doc) AS (
  SELECT CAST(readfile('{current_path}') AS TEXT)
), previous_doc(doc) AS (
  SELECT CAST(readfile('{previous_path}') AS TEXT)
), current_rows AS (
  SELECT json_extract(value, '$.story') AS story,
         json_extract(value, '$.slug') AS slug,
         json_extract(value, '$.presentations') AS presentations,
         json_extract(value, '$.views') AS views,
         json_extract(value, '$.reads') AS reads,
         CASE WHEN json_extract(value, '$.views') = 0 THEN 0 ELSE json_extract(value, '$.reads') * 1.0 / json_extract(value, '$.views') END AS read_ratio
  FROM current_doc, json_each(current_doc.doc, '$.scopes.storyLifetime')
), previous_rows AS (
  SELECT json_extract(value, '$.slug') AS slug,
         json_extract(value, '$.views') AS views,
         json_extract(value, '$.reads') AS reads
  FROM previous_doc, json_each(previous_doc.doc, '$.scopes.storyLifetime')
)
SELECT current_rows.*,
       current_rows.views - previous_rows.views AS delta_views_vs_previous,
       current_rows.reads - previous_rows.reads AS delta_reads_vs_previous
FROM current_rows
LEFT JOIN previous_rows USING (slug)""",
                "description": "Reproducible story-level scorecard generated from the current signed-in Medium snapshot, the prior snapshot, and the reviewed Medium content inventory.",
                "executed_at": captured_at,
                "tables_used": [current_path, previous_path, "analytics/medium-content-inventory-2026-09-03.json"],
                "filters": ["Account: @singhaditya21_89007", "Published Medium stories only for performance metrics", "Scheduled Medium stories shown separately"],
                "metric_definitions": [
                    "Portfolio read ratio = sum of lifetime reads divided by sum of lifetime views across published stories.",
                    "Story read ratio = lifetime reads divided by lifetime views; zero when views are zero.",
                    "Seven-day checkpoint pass = at least 5 presentations, 3 views, and 1 read for a story published at least 7 calendar days before capture.",
                    "Evidence maturity is Nascent below 5 views, Early from 5 through 19 views, and Decision-ready at 20 or more views.",
                    "Review lanes are diagnostic rules for this account, not universal Medium benchmarks."
                ]
            }
        },
        {
            "id": "medium_current_stats",
            "label": "Medium Stats · September 2026 and story lifetime",
            "path": current_path,
            "query": {
                "engine": "sqlite",
                "language": "sql",
                "sql": f"WITH source(doc) AS (SELECT CAST(readfile('{current_path}') AS TEXT)) SELECT json_extract(doc, '$.scopes.currentMonth.presentations') AS september_presentations, json_extract(doc, '$.scopes.currentMonth.views') AS september_views, json_extract(doc, '$.scopes.currentMonth.reads') AS september_reads, json_extract(doc, '$.scopes.audienceLifetime.followers') AS followers, json_extract(doc, '$.scopes.audienceLifetime.emailSubscribers') AS email_subscribers FROM source",
                "description": "Read-only capture from the signed-in Medium Stories and Audience statistics pages.",
                "executed_at": captured_at,
                "tables_used": ["Medium Stats > Stories", "Medium Stats > Audience"],
                "filters": ["September 1–4, 2026 UTC for monthly totals", "Lifetime for story rows and audience totals"],
                "metric_definitions": [
                    "Presentations = Medium's tracked suggestions of a story on eligible Medium surfaces.",
                    "Views = readers who accessed a story and remained for at least five seconds.",
                    "Reads = readers who remained for at least thirty seconds."
                ]
            }
        },
        {
            "id": "medium_inventory",
            "label": "Medium content inventory · September 3, 2026",
            "path": "analytics/medium-content-inventory-2026-09-03.json",
            "query": {
                "engine": "sqlite",
                "language": "sql",
                "sql": "WITH inventory(doc) AS (SELECT CAST(readfile('analytics/medium-content-inventory-2026-09-03.json') AS TEXT)) SELECT json_extract(value, '$.title') AS story, json_extract(value, '$.scheduleAt') AS scheduled_at, json_extract(value, '$.subscriberEmail') AS subscriber_email, json_extract(value, '$.paywall') AS paywall FROM inventory, json_each(inventory.doc, '$.scheduled')",
                "description": "Reviewed published and scheduled Medium story inventory with public URLs, publication placement, schedule, subscriber-email and paywall state.",
                "executed_at": "2026-09-03T14:22:25+05:30",
                "tables_used": ["analytics/medium-content-inventory-2026-09-03.json"],
                "filters": ["Published and scheduled Medium stories"]
            }
        },
        {
            "id": "medium_metric_definitions",
            "label": "Medium Help Center · Stats definitions",
            "href": "https://help.medium.com/hc/en-us/articles/215108608-Stats",
            "query": {
                "engine": "official documentation",
                "description": "Medium's current definitions and update cadence for presentations, views, reads, followers and subscribers.",
                "executed_at": captured_at,
                "tables_used": ["Medium Help Center > Stats"]
            }
        }
    ]


def build_scorecard() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    baseline = load_json(BASELINE)
    inventory = load_json(INVENTORY)
    snapshot_paths = sorted(SNAPSHOTS_DIR.glob("*.json"))
    if len(snapshot_paths) < 2:
        raise SystemExit("at least two dated Medium snapshots are required")
    current_path = snapshot_paths[-1]
    previous_path = snapshot_paths[-2]
    current = load_json(current_path)
    previous = load_json(previous_path)
    if baseline["capturedAt"] != current["capturedAt"] or baseline["scopes"] != current["scopes"]:
        raise SystemExit("engagement-baseline.json must match the latest dated snapshot")

    capture_date = datetime.fromisoformat(current["capturedAt"].replace("Z", "+00:00")).date()
    published_index = {normalized_title(item["title"]): item for item in inventory["published"]}
    previous_rows = {item["slug"]: item for item in previous["scopes"]["storyLifetime"]}
    story_rows: list[dict[str, Any]] = []

    for item in current["scopes"]["storyLifetime"]:
        metadata = published_index.get(normalized_title(item["story"]))
        if metadata is None:
            raise SystemExit(f"published inventory is missing {item['story']}")
        published_date = parse_published_date(metadata["publishedLabel"])
        age_days = (capture_date - published_date).days
        views = item["views"]
        reads = item["reads"]
        read_ratio = reads / views if views else 0.0
        lane, priority, next_action = classify_story(age_days, item["presentations"], views, reads, read_ratio)
        prior = previous_rows.get(item["slug"])
        story_rows.append({
            "story": item["story"],
            "slug": item["slug"],
            "published_at": published_date.isoformat(),
            "age_days": age_days,
            "publication": metadata["publication"] or "Independent",
            "public_url": metadata["url"],
            "presentations": item["presentations"],
            "views": views,
            "reads": reads,
            "read_ratio": round(read_ratio, 4),
            "views_per_presentation": round(views / item["presentations"], 4) if item["presentations"] else None,
            "delta_views_vs_previous": views - prior["views"] if prior else None,
            "delta_reads_vs_previous": reads - prior["reads"] if prior else None,
            "checkpoint_7d": checkpoint_status(age_days, item["presentations"], views, reads),
            "evidence_maturity": evidence_maturity(views),
            "review_lane": lane,
            "priority": priority,
            "next_action": next_action
        })

    story_rows.sort(key=lambda row: (row["reads"], row["views"], row["presentations"]), reverse=True)
    presentations = sum(row["presentations"] for row in story_rows)
    views = sum(row["views"] for row in story_rows)
    reads = sum(row["reads"] for row in story_rows)
    stories_with_reads = sum(row["reads"] > 0 for row in story_rows)
    eligible = [row for row in story_rows if row["checkpoint_7d"] != "Not due"]
    checkpoint_passes = sum(row["checkpoint_7d"] == "Pass" for row in eligible)
    top_three_reads = sum(row["reads"] for row in story_rows[:3])
    common_slugs = set(previous_rows)
    delta_common_reads = sum(row["reads"] for row in story_rows if row["slug"] in common_slugs) - sum(row["reads"] for row in previous_rows.values())

    account = current["scopes"]["currentMonth"]
    audience = current["scopes"]["audienceLifetime"]
    summary = {
        "published_stories": len(story_rows),
        "scheduled_stories": len(inventory["scheduled"]),
        "lifetime_presentations": presentations,
        "lifetime_views": views,
        "lifetime_reads": reads,
        "portfolio_read_ratio": round(reads / views, 4) if views else 0.0,
        "stories_with_reads": stories_with_reads,
        "stories_with_reads_share": round(stories_with_reads / len(story_rows), 4),
        "zero_read_stories": len(story_rows) - stories_with_reads,
        "eligible_7d_stories": len(eligible),
        "checkpoint_7d_passes": checkpoint_passes,
        "checkpoint_7d_pass_rate": round(checkpoint_passes / len(eligible), 4) if eligible else 0.0,
        "top_three_reads": top_three_reads,
        "top_three_read_share": round(top_three_reads / reads, 4) if reads else 0.0,
        "delta_common_reads_vs_previous": delta_common_reads,
        "september_presentations": account["presentations"],
        "september_views": account["views"],
        "september_reads": account["reads"],
        "followers": audience["followers"],
        "email_subscribers": audience["emailSubscribers"]
    }

    scheduled_rows: list[dict[str, Any]] = []
    for item in inventory["scheduled"]:
        scheduled_at = datetime.fromisoformat(item["scheduleAt"])
        scheduled_rows.append({
            "story": item["title"],
            "scheduled_at": friendly_datetime(scheduled_at),
            "subscriber_email": "On" if item["subscriberEmail"] else "Off",
            "paywall": "On" if item["paywall"] else "Off",
            "checkpoint_48h": friendly_datetime(scheduled_at + timedelta(days=2)),
            "checkpoint_7d": friendly_datetime(scheduled_at + timedelta(days=7)),
            "checkpoint_28d": friendly_datetime(scheduled_at + timedelta(days=28))
        })

    current_rel = str(current_path.relative_to(ROOT))
    previous_rel = str(previous_path.relative_to(ROOT))
    sources = source_objects(current["capturedAt"], current_rel, previous_rel)
    title = "Medium Story Performance Scorecard"
    cards = [
        {"id": "lifetime_reads", "description": "Total reads across the 11 published stories; this is a portfolio sum of lifetime story counts.", "dataset": "portfolio_summary", "sourceId": "scorecard_summary", "metrics": [{"label": "Lifetime reads", "field": "lifetime_reads", "format": "number"}, {"label": "Δ on Aug 31 catalog", "field": "delta_common_reads_vs_previous", "format": "number", "signed": True}]},
        {"id": "portfolio_read_ratio", "description": "Lifetime reads divided by lifetime views across the published catalog.", "dataset": "portfolio_summary", "sourceId": "scorecard_summary", "metrics": [{"label": "Portfolio read ratio", "field": "portfolio_read_ratio", "format": "percent"}, {"label": "Views", "field": "lifetime_views", "format": "number"}]},
        {"id": "stories_with_reads", "description": "Published stories that have produced at least one lifetime read.", "dataset": "portfolio_summary", "sourceId": "scorecard_summary", "metrics": [{"label": "Stories with a read", "field": "stories_with_reads", "format": "number"}, {"label": "Share of catalog", "field": "stories_with_reads_share", "format": "percent"}]},
        {"id": "checkpoint_pass_rate", "description": "Stories at least seven days old meeting the account-specific floor of 5 presentations, 3 views and 1 read.", "dataset": "portfolio_summary", "sourceId": "scorecard_summary", "metrics": [{"label": "7-day floor pass", "field": "checkpoint_7d_pass_rate", "format": "percent"}, {"label": "Eligible stories", "field": "eligible_7d_stories", "format": "number"}]},
        {"id": "september_reads", "description": "Reads recorded from September 1 through September 4, 2026 UTC; this is a partial-month actual.", "dataset": "portfolio_summary", "sourceId": "medium_current_stats", "metrics": [{"label": "September reads", "field": "september_reads", "format": "number"}, {"label": "September views", "field": "september_views", "format": "number"}]}
    ]
    charts = [{
        "id": "lifetime_reads_by_story",
        "title": "Lifetime reads by published story",
        "subtitle": "The top three stories contribute 14 of 17 lifetime reads; no story has reached 20 views.",
        "intent": "comparison",
        "question": "Which published stories have converted available traffic into reads?",
        "rationale": "A sorted horizontal bar keeps long story titles readable and makes the portfolio concentration visible.",
        "comparisonContext": {"denominator": "Lifetime story reads", "grain": "published story", "unit": "reads"},
        "type": "horizontalBar",
        "dataset": "story_lifetime",
        "sourceId": "scorecard_inputs",
        "encodings": {
            "x": {"field": "story", "type": "nominal", "label": "Story"},
            "y": {"field": "reads", "type": "quantitative", "label": "Reads", "format": "number"},
            "tooltip": [
                {"field": "presentations", "type": "quantitative", "label": "Presentations", "format": "number"},
                {"field": "views", "type": "quantitative", "label": "Views", "format": "number"},
                {"field": "read_ratio", "type": "quantitative", "label": "Read ratio", "format": "percent"},
                {"field": "review_lane", "type": "nominal", "label": "Review lane"}
            ]
        },
        "valueFormat": "number",
        "layout": "full",
        "labels": {"values": "all"},
        "palette": {"kind": "sequential", "name": "blue"},
        "settings": {"sort": "descending", "showValues": True}
    }]
    tables = [
        {
            "id": "published_story_scorecard",
            "title": "Published story scorecard",
            "subtitle": "Lifetime metrics captured September 4, 2026; review lane applies the account-specific decision rules.",
            "dataset": "story_lifetime",
            "sourceId": "scorecard_inputs",
            "defaultSort": {"field": "reads", "direction": "desc"},
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "story", "label": "Story", "type": "text"},
                {"field": "published_at", "label": "Published", "type": "date"},
                {"field": "publication", "label": "Placement", "type": "text"},
                {"field": "presentations", "label": "Presentations", "format": "number"},
                {"field": "views", "label": "Views", "format": "number"},
                {"field": "reads", "label": "Reads", "format": "number"},
                {"field": "read_ratio", "label": "Read ratio", "format": "percent"},
                {"field": "delta_views_vs_previous", "label": "Δ views", "format": "number", "movement": True},
                {"field": "delta_reads_vs_previous", "label": "Δ reads", "format": "number", "movement": True},
                {"field": "checkpoint_7d", "label": "7-day floor", "type": "text"},
                {"field": "evidence_maturity", "label": "Evidence", "type": "text"},
                {"field": "review_lane", "label": "Review lane", "type": "text"}
            ]
        },
        {
            "id": "scheduled_story_checkpoints",
            "title": "Scheduled story checkpoints",
            "subtitle": "Scheduled Medium releases and the next three measurement checkpoints, all in IST.",
            "dataset": "scheduled_stories",
            "sourceId": "medium_inventory",
            "defaultSort": {"field": "scheduled_at", "direction": "asc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "story", "label": "Story", "type": "text"},
                {"field": "scheduled_at", "label": "Release", "type": "text"},
                {"field": "subscriber_email", "label": "Email", "type": "text"},
                {"field": "paywall", "label": "Paywall", "type": "text"},
                {"field": "checkpoint_48h", "label": "48-hour", "type": "text"},
                {"field": "checkpoint_7d", "label": "7-day", "type": "text"},
                {"field": "checkpoint_28d", "label": "28-day", "type": "text"}
            ]
        }
    ]
    blocks = [
        {"id": "report_title", "type": "markdown", "body": f"# {title}"},
        {"id": "executive_summary", "type": "markdown", "body": "## Executive Summary\n\n- **Only 5 of 11 published stories have produced a read.** The catalog has 75 lifetime presentations, 53 views and 17 reads, for a 32.1% portfolio read ratio.\n- **Reading is concentrated in three proven stories.** The two CRM architecture stories and *Why Traditional CRM Will Die Without Agentic AI* contribute 14 of 17 reads (82.4%).\n- **Four mature stories require intervention, but no body rewrite is yet evidence-backed.** Five of nine seven-day-eligible stories meet the provisional floor; no story has reached the 20-view minimum used here for a confident retention decision.\n- **September discovery has not converted yet.** The partial month shows 8 views and 0 reads, while the audience remains 3 followers and 2 email subscribers."},
        {"id": "headline_metrics", "type": "metric-strip", "cardIds": ["lifetime_reads", "portfolio_read_ratio", "stories_with_reads", "checkpoint_pass_rate", "september_reads"]},
        {"id": "portfolio_concentration", "type": "markdown", "sourceId": "scorecard_inputs", "body": "## Three stories carry most reading depth\n\n**The working pattern is concrete architecture with a bounded enterprise problem.** *How to Build an Agentic CRM* and *Why Traditional CRM Will Die Without Agentic AI* have 5 reads each; *The Enterprise Agent Control Tower* has 4. Together they generate 82.4% of all lifetime reads. Reuse their faster problem framing, concrete system boundary and navigable architecture pattern in the next releases—but treat the result as a directional signal because every story has fewer than 20 views."},
        {"id": "lifetime_reads_chart", "type": "chart", "chartId": "lifetime_reads_by_story", "layout": "full"},
        {"id": "intervention_lanes", "type": "markdown", "sourceId": "scorecard_inputs", "body": "## Four mature stories need different fixes\n\n- **Distribution:** *Your AI Agent’s Memory Is a Database, Not a Prompt* has 3 presentations, 1 view and 0 reads. Audit topics, visibility and publication fit before changing its body.\n- **Packaging:** *Human Approval Is a Queueing System* has 5 presentations and 0 views; the $2.4M escalation story has 6 presentations and 0 views. Their title, subtitle and hero are the first testable levers.\n- **Early retention signal:** *Every AI Agent Action Needs a Receipt* has 9 views and 0 reads. Inspect its traffic and first screen now, but wait for 20 views before a structural rewrite.\n- **Monitor:** *Model Routing Is Capital Allocation* and *Your Multi-Agent System Is a Distributed System* are still inside their first seven days and should remain unchanged until their checkpoints."},
        {"id": "published_story_table", "type": "table", "tableId": "published_story_scorecard", "layout": "full"},
        {"id": "scheduled_pipeline", "type": "markdown", "sourceId": "medium_inventory", "body": "## Three scheduled stories have clean measurement gates\n\nAll three scheduled releases have subscriber email enabled and paywall disabled. Capture the same presentation → view → read funnel at 48 hours, 7 days and 28 days; do not mix their pre-publication state into the published-story scorecard."},
        {"id": "scheduled_story_table", "type": "table", "tableId": "scheduled_story_checkpoints", "layout": "full"},
        {"id": "recommended_next_steps", "type": "markdown", "body": "## Recommended next steps\n\n1. Audit the topics, visibility and publication eligibility of the Memory story.\n2. Prepare one title/subtitle/hero test each for Human Approval and the $2.4M escalation story; apply only after reviewing exact variants.\n3. Inspect detailed traffic sources and the first screen of Action Receipt; hold the body until it reaches 20 views or a seven-day review confirms the same signal.\n4. Copy the structural strengths of the three read leaders into the scheduled stories without changing their approved thesis or schedule.\n5. Refresh this scorecard after every 48-hour, 7-day and 28-day checkpoint."},
        {"id": "further_questions", "type": "markdown", "body": "## Further questions\n\n- Which traffic sources produced the nine Action Receipt views?\n- Do feed clickthrough, story-attributed follows or story-attributed subscribers appear once Medium has enough data?\n- Does the next scheduled release generate its first read within seven days?"},
        {"id": "caveats", "type": "markdown", "body": "## Caveats and assumptions\n\n- September is a partial month; it is not compared with the complete August period.\n- Story metrics are lifetime values, while September totals are monthly; the two scopes are not reconciled.\n- Views divided by presentations is not Medium feed clickthrough because views can originate outside tracked presentation surfaces.\n- All performance rates are directional: no story has reached 20 views.\n- The 5-presentation, 3-view, 1-read seven-day floor and 20-view retention gate are account-specific operating thresholds, not Medium benchmarks.\n- The 12 GitHub-only future stories are excluded because they are not yet Medium stories."}
    ]
    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": title,
            "description": "An action-oriented review of every published and scheduled Medium story, using current lifetime metrics and account-specific decision thresholds.",
            "generatedAt": current["capturedAt"],
            "cards": cards,
            "charts": charts,
            "tables": tables,
            "sources": sources,
            "blocks": blocks
        },
        "snapshot": {
            "version": 1,
            "generatedAt": current["capturedAt"],
            "status": "ready",
            "datasets": {"portfolio_summary": [summary], "story_lifetime": story_rows, "scheduled_stories": scheduled_rows}
        },
        "sources": sources,
        "package_info": {"root": "analytics", "manifestPath": "analytics/engagement-dashboard.artifact.json", "snapshotPath": current_rel}
    }
    return artifact, story_rows, scheduled_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "metrics-report")
    parser.add_argument("--artifact-output", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    artifact, story_rows, scheduled_rows, summary = build_scorecard()
    args.artifact_output.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    story_fields = [
        "story", "slug", "published_at", "age_days", "publication", "public_url", "presentations", "views", "reads",
        "read_ratio", "views_per_presentation", "delta_views_vs_previous", "delta_reads_vs_previous", "checkpoint_7d",
        "evidence_maturity", "review_lane", "priority", "next_action"
    ]
    with (args.output_dir / "story-metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=story_fields)
        writer.writeheader()
        writer.writerows(story_rows)
    with (args.output_dir / "scheduled-story-checkpoints.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scheduled_rows[0]))
        writer.writeheader()
        writer.writerows(scheduled_rows)

    summary_lines = [
        "# Medium story performance scorecard",
        "",
        f"Snapshot: {artifact['snapshot']['generatedAt']}",
        "",
        f"- Published stories: {summary['published_stories']}",
        f"- Lifetime portfolio: {summary['lifetime_presentations']} presentations, {summary['lifetime_views']} views, {summary['lifetime_reads']} reads",
        f"- Portfolio read ratio: {summary['portfolio_read_ratio']:.1%}",
        f"- Stories with at least one read: {summary['stories_with_reads']} of {summary['published_stories']}",
        f"- Seven-day floor: {summary['checkpoint_7d_passes']} of {summary['eligible_7d_stories']} eligible stories passed",
        f"- Scheduled stories: {summary['scheduled_stories']}",
        "",
        "The interactive report is delivered through the Data Analytics artifact; these files preserve the reproducible scorecard inputs and exact rows."
    ]
    (args.output_dir / "engagement-summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    (args.output_dir / "engagement-dashboard.artifact.json").write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"built Medium scorecard for {len(story_rows)} published and {len(scheduled_rows)} scheduled stories")


if __name__ == "__main__":
    main()
