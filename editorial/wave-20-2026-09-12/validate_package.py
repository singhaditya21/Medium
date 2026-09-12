#!/usr/bin/env python3
"""Read-only structural QA. Does not certify editorial quality or publish anything."""
import ast
import hashlib
import json
import math
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
manifest = json.loads((HERE / "manifest.json").read_text())
inventory = json.loads((HERE / "review-inventory.json").read_text())
items = manifest["existing"] + manifest["new"]
assert len(items) == len(inventory) == 20
assert len(manifest["existing"]) == 12 and len(manifest["new"]) == 8
assert len({i["id"] for i in items}) == len({i["slug"] for i in items}) == 20
assert sum(r["figureCount"] for r in inventory) == 44
assert len(list((HERE / "preview").glob("*.html"))) == 20
posts = (HERE / "linkedin-posts.md").read_text()
checked_images = 0
checked_links = 0
checked_code = 0


class LocalLinks(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.source = source

    def handle_starttag(self, tag, attrs):
        global checked_links
        for attr, value in attrs:
            if attr not in {"src", "href"} or not value:
                continue
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (ROOT if parsed.path.startswith("/") else self.source.parent)
            target = target / unquote(parsed.path.lstrip("/"))
            assert target.exists(), f"Broken local link: {self.source.name} -> {value}"
            checked_links += 1


for index, (item, record) in enumerate(zip(items, inventory)):
    assert item["id"] == record["id"]
    source_path = ROOT / item["source"]
    source = source_path.read_text()
    assert hashlib.sha256(source.encode()).hexdigest() == record["sourceSha256"]
    assert len(record["topics"]) == len(set(record["topics"])) == 5
    assert record["subscriberEmail"] is True and record["paywall"] is False
    assert record["mediumUrl"] is None and record["publication"] is None
    assert record["status"] == "draft_human_review_required"
    medium_day = date.fromisoformat(record["mediumDate"])
    linkedin_day = date.fromisoformat(record["linkedinDate"])
    assert medium_day.weekday() in {0, 3}
    assert medium_day > date(2026, 10, 9)
    assert linkedin_day == medium_day + timedelta(days=1)
    if index:
        previous = date.fromisoformat(inventory[index - 1]["mediumDate"])
        assert (medium_day - previous).days in {3, 4}
    section = posts.split(f"## {item['id']} — ", 1)[1].split("\n## ", 1)[0]
    post = section.split("\n\n", 2)[2].split("\n\n**Finalization gate:", 1)[0]
    assert hashlib.sha256(post.encode()).hexdigest() == record["linkedinTextSha256"]
    assert len(post) < 2800
    assert not re.search(r"\b(?:ghp_|sk-proj-)[A-Za-z0-9]{16,}", source + post)
    if index < 12:
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{item['source']}"], cwd=ROOT
        )
        assert committed == source_path.read_bytes(), "Existing story body changed"
        assert record["canonical"].startswith("https://singhaditya21.github.io/Medium/")
    else:
        assert record["canonical"] is None
        assert "This story was developed with AI" in source[:800]
        assert "AI-assisted reference" in source
        assert 650 <= record["wordCount"] <= 900
        fences = re.findall(r"^~~~.*$", source, re.MULTILINE)
        assert len(fences) % 2 == 0
        for language, code in re.findall(r"^~~~(\w+)\n(.*?)^~~~$", source, re.MULTILINE | re.DOTALL):
            if language == "json":
                json.loads(code)
                checked_code += 1
            elif language == "python":
                ast.parse(code)
                checked_code += 1
        svg = ROOT / item["hero"]
        ET.parse(svg)
        png = svg.with_suffix(".png").read_bytes()
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", png[16:24]) == (1600, 1040)
        checked_images += 1

for html in [HERE / "preview.html", *(HERE / "preview").glob("*.html")]:
    LocalLinks(html).feed(html.read_text())

queue = json.loads((ROOT / "engagement/queue.json").read_text())
batch = [c for c in queue["candidates"] if c["id"].startswith("2026-09-12-linkedin-comment-c")]
assert len(batch) == 5
research = (ROOT / "engagement/linkedin-20-opportunities-2026-09-12.md").read_text()
assert len(re.findall(r"^\| (?:C[1-5]|B\d{2}) \|", research, re.MULTILINE)) == 20
for candidate in batch:
    assert candidate["state"] == "ready_for_confirmation"
    assert candidate["draftResponse"] in research
    assert candidate["targetUrl"] in research
    assert candidate["priorityScore"] >= .70

# Verify illustrative arithmetic, not real-world estimates or causal validity.
assert 3 * 2 * 4 == 24
assert 100 * .10 * 5 == 50
assert math.isclose(20 / 7000 * 100, .2857142857142857)
assert round(50000 / 50200 * 100, 3) == 99.602
assert round(400 / 12000 * 100, 2) == 3.33
assert 400 - 70 == 330

print(json.dumps({
    "result": "pass", "stories": 20, "newStories": 8,
    "linkedinDrafts": 20, "publicPostLeads": 20, "approvalReadyComments": 5,
    "newSvgPngPairsChecked": checked_images, "localLinksChecked": checked_links,
    "codeBlocksSyntaxChecked": checked_code,
    "limitation": "Structural checks only; editorial review, media finalization and approval remain."
}, indent=2))
