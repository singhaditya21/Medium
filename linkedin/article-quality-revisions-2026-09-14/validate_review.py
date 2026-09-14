"""Validate the local review package without contacting either publishing platform."""
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags, self.links, self.images, self.lists = [], [], [], []
        self.in_li = False
        self.li = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        assert not any(key.startswith("on") for key in attrs), "Inline event handler"
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "img":
            assert attrs.get("alt", "").strip(), "Missing image alternative text"
            self.images.append(attrs["src"])
        if tag == "li":
            self.in_li, self.li = True, []

    def handle_data(self, data):
        if self.in_li:
            self.li.append(data)

    def handle_endtag(self, tag):
        if tag == "li":
            self.lists.append("".join(self.li))
            self.in_li = False


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_links(document):
    for ref in document.links + document.images:
        parts = urlsplit(ref)
        assert parts.scheme not in {"javascript", "data", "file"}, ref
        if not parts.scheme and parts.path:
            assert (ROOT / unescape(parts.path)).is_file(), "Missing local target: " + ref
        if parts.scheme:
            assert parts.scheme == "https", "Unexpected remote URL scheme: " + ref
            assert not parts.username and not parts.password, "Credential-bearing URL"
            assert not re.search(r"/(messaging|edit|drafts)(/|\?|$)", ref), "Private/edit URL"


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["status"] == "review_drafts_not_applied"
    assert manifest["external_mutations"] == []
    assert len(manifest["articles"]) == 4 and len(manifest["figures"]) == 3
    baseline = (ROOT / manifest["baseline"]["path"]).read_bytes()
    assert digest(baseline) == manifest["baseline"]["sha256"]
    docs = {}
    for spec in manifest["articles"]:
        raw = (ROOT / spec["preview"]).read_bytes()
        text = raw.decode()
        assert digest(raw) == spec["preview_sha256"], spec["preview"]
        body = re.search(r"<article>([\s\S]*?)</article>", text).group(1)
        body = body.replace('<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable data table"><table>', '<table>').replace('</table></div>', '</table>')
        assert digest(body.encode()) == spec["body_sha256"], spec["id"]
        doc = Document(body)
        assert doc.tags.count("h1") == 1
        assert not set(doc.tags).intersection({"script", "iframe", "form", "input", "button"})
        assert len(doc.images) == spec["figures"]
        assert "REVISED DRAFT · NOT APPLIED TO LINKEDIN OR MEDIUM" in text
        check_links(Document(text))
        docs[spec["id"]] = doc
    original = Document(baseline.decode())
    assert len(original.images) == len(docs["Q2"].images) == 10
    assert len(original.lists) == len(docs["Q2"].lists)
    expected_lists = [item.replace(
        'idempotency keys so retries do not send the same email or issue the same refund twice;',
        'domain-enforced idempotency contracts and stable action identifiers for supported retries;')
        for item in original.lists]
    assert docs["Q2"].lists == expected_lists, "Unexpected CRM list change"
    for i, (old, new) in enumerate(zip(original.images, docs["Q2"].images), 1):
        if i not in (4, 5):
            assert old == new, "Unexpected CRM figure replacement"
    for fig in manifest["figures"]:
        svg = (ROOT / fig["svg"]).read_bytes()
        png = (ROOT / fig["png"]).read_bytes()
        assert digest(svg) == fig["svg_sha256"]
        assert digest(png) == fig["png_sha256"]
        assert png.startswith(b"\x89PNG\r\n\x1a\n")
        tree = ET.fromstring(svg)
        assert tree.find("{http://www.w3.org/2000/svg}title") is not None
        assert tree.find("{http://www.w3.org/2000/svg}desc") is not None
        assert fig["width"] > 1500 and fig["height"] > 2500
    check_links(Document((ROOT / "index.html").read_text()))
    snippets = 0
    for name in ("Q1-passport.md", "Q2-contract-insertion.md", "Q3-accuracy.md", "Q4-three-minute.md"):
        md = (ROOT / name).read_text()
        for language, code in re.findall(r"```(python|json)\n([\s\S]*?)\n```", md):
            snippets += 1
            if language == "json":
                json.loads(code)
            else:
                env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1")
                with tempfile.TemporaryDirectory() as work:
                    subprocess.run([sys.executable, "-c", code], cwd=work, env=env, check=True)
    assert snippets == 3, "Unexpected runnable/JSON snippet count"
    forbidden = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{10,}|-----BEGIN (?:RSA )?PRIVATE KEY-----")
    for name in ROOT.rglob("*"):
        if name.suffix in {".html", ".md", ".json", ".svg", ".py", ".mjs"}:
            assert not forbidden.search(name.read_text()), "Possible secret: " + str(name)
    print(json.dumps({"status": "PASS", "articles": 4, "new_figures": 3,
                      "retained_crm_figures": 8, "runnable_python_examples": 2,
                      "valid_json_examples": 1, "live_changes": 0}))


if __name__ == "__main__":
    main()
