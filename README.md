# Medium

A static publishing and distribution system for Aditya Singh’s essays on enterprise AI, agent architecture, identity, governance, economics, and CRM.

**Live site:** <https://singhaditya21.github.io/Medium/>  
**Original publication:** <https://medium.com/@singhaditya21_89007>

## What is included

- One responsive, accessible page for each published story
- Locally archived article figures and diagrams
- Searchable story index, guided reading series, dark mode, reading progress, related stories, and article navigation
- Human-triggered share links with UTM parameters and a GitHub Discussions handoff
- Article and collection JSON-LD, sitemap, robots file, Atom/RSS/JSON feeds, and canonical links
- Snapshot data in `data/` and a repeatable static-site builder
- Review-only distribution packs, weekly editorial briefs, live health checks, Lighthouse budgets, and a source-backed engagement dashboard

## Build locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_site.py
python scripts/validate_site.py
python scripts/stage_pages.py
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

The builder reads captured story data from `data/*.json`, downloads any missing figures into `assets/images/`, and regenerates the index, article pages, series pages, feeds, sitemap, robots file, and story manifest. `stage_pages.py` creates a clean `_site/` directory containing public files only.

## Editorial growth system

The repository supports a deliberate weekly loop without automating Medium or social interactions:

1. `distribution-pack.yml` generates channel drafts, import checks, topics, publication-submission checks, and a manual release gate. A newly added story gets a GitHub review issue.
2. `weekly-editorial.yml` opens one Monday issue that rotates through the catalog and assigns a single flagship story.
3. The author reviews claims, disclosure, canonical settings, and channel-specific wording before manually publishing or submitting anything.
4. `metrics-report.yml` packages the latest reviewed Medium snapshot and opens a monthly manual-refresh issue.

Generate the same assets locally:

```bash
python scripts/generate_distribution_pack.py --all
python scripts/generate_weekly_editorial.py
python scripts/generate_metrics_report.py
```

Generated working directories are ignored by Git. The source-backed dashboard is kept in `analytics/engagement-dashboard.html`; it is an operator artifact and is deliberately excluded from the GitHub Pages deployment.

## Privacy-friendly analytics

Page analytics are disabled by default. The site builder emits a zero-cookie-compatible analytics script only when both GitHub Actions repository variables are configured:

- `SITE_ANALYTICS_SCRIPT_URL`: the HTTPS script URL supplied by the selected provider
- `SITE_ANALYTICS_WEBSITE_ID`: the provider’s public website identifier

This works with a privacy-friendly provider such as a self-hosted Umami instance. Provider signup, data residency, retention, and consent requirements must be reviewed before enabling it. Never store Medium cookies or credentials in these variables.

## Automation boundaries

GitHub Actions improves discoverability, quality, measurement, and editorial consistency. It does **not** generate artificial traffic or perform account interactions. The workflows do not clap, follow, highlight, respond, repost, submit to publications, scrape signed-in Medium pages, or store Medium session data. Public posts and publication submissions remain explicit human actions.

## Publishing

GitHub Actions rebuilds, validates, stages, and deploys the repository on every push to `main`. Action dependencies are pinned to full commit SHAs. The deployment publishes `_site/`, not the repository root, so source data, scripts, reports, and workflow files are not served as website pages.

Quality workflows:

- `content-ci.yml`: compiles scripts, builds, validates story metadata and local links, stages the public site, and uploads review-only distribution packs
- `site-health.yml`: verifies the generated archive and live GitHub Pages URLs every Wednesday
- `performance.yml`: enforces Lighthouse thresholds after deployment and every Friday
- `metrics-report.yml`: validates the checked-in engagement snapshot and packages the dashboard monthly or on demand

## Content rights

All article text and original diagrams are © Aditya Singh. Canonical Medium links are preserved on every article page. Third-party references linked from the essays remain the property of their respective owners.
