# Medium

A static archive of Aditya Singh’s published Medium essays on enterprise AI, agent architecture, identity, governance, economics, and CRM.

**Live site:** <https://singhaditya21.github.io/Medium/>  
**Original publication:** <https://medium.com/@singhaditya21_89007>

## What is included

- One responsive, accessible page for each published story
- Locally archived article figures and diagrams
- Searchable story index, dark mode, reading progress, and article navigation
- SEO metadata, sitemap, robots file, and canonical links to the original Medium stories
- Snapshot data in `data/` and a repeatable static-site builder

## Build locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_site.py
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

The builder reads the captured story data from `data/*.json`, downloads any missing figures into `assets/images/`, and regenerates the index, article pages, sitemap, robots file, and story manifest.

## Publishing

GitHub Actions deploys the repository to GitHub Pages on every push to `main`. The workflow publishes the static files directly; no runtime or database is required.

## Content rights

All article text and original diagrams are © Aditya Singh. Canonical Medium links are preserved on every article page. Third-party references linked from the essays remain the property of their respective owners.
