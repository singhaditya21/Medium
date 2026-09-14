#!/usr/bin/env python3
"""Build review-only N02–N04 editions. No network or publishing capability."""
import copy
import hashlib
import html
import json
from pathlib import Path
import re
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "linkedin/newsletter-backfill-2026-09-14"


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"p", "li", "ul", "ol", "pre", "h2", "h3"}:
            self.parts.append("\n")


def plain(markup):
    parser = TextParser()
    parser.feed(markup)
    return "".join(parser.parts)


def norm(value):
    return re.sub(r"\s+", " ", value).strip()


def fnv(value):
    result = 2166136261
    raw = value.encode("utf-16-le")
    for i in range(0, len(raw), 2):
        result = ((result ^ int.from_bytes(raw[i:i+2], "little")) * 16777619) & 0xFFFFFFFF
    return f"{result:08x}"


def block_text(block, source_figure_text=True):
    if block.get("type") == "figure":
        return norm(block.get("caption", "")) if source_figure_text else ""
    return norm(block.get("text", plain(block.get("html", ""))))


def text_block(tag, text, href=None):
    markup = html.escape(text)
    if href:
        markup = f'<a href="{html.escape(href, quote=True)}">{markup}</a>'
    return {"type": "html", "tag": tag, "text": text, "html": markup}


def find_anchor(blocks, text, occurrence=None):
    matches = [i for i, b in enumerate(blocks) if block_text(b) == norm(text)]
    if occurrence is not None and 1 <= occurrence <= len(matches):
        return matches[occurrence - 1]
    if len(matches) != 1:
        raise ValueError(f"Anchor must match exactly once ({len(matches)}): {text}")
    return matches[0]


def reconcile(archive, rules):
    blocks = copy.deepcopy(archive["blocks"])
    if rules.get("subtitle"):
        blocks.insert(0, text_block("h2", rules["subtitle"]))
    for addition in rules.get("insertions", []):
        blocks.insert(find_anchor(blocks, addition["before"]), text_block(addition["tag"], addition["text"]))
    for entry in rules["lists"]:
        anchor, tag, items = entry[:3]
        occurrence = entry[3] if len(entry) == 4 else None
        blocks.insert(find_anchor(blocks, anchor, occurrence) + 1, {
            "type": "html", "tag": tag, "text": " ".join(items),
            "html": "".join(f"<li>{html.escape(item)}</li>" for item in items),
            "items": items,
        })
    for addition in rules.get("append", []):
        blocks.append(text_block(addition["tag"], addition["text"], addition.get("href")))
    for anchor, tag in rules.get("tagRepairs", []):
        blocks[find_anchor(blocks, anchor)]["tag"] = tag
    return blocks


def render_block(block, slug, figure_number, figure_directory=None):
    if block["type"] == "figure":
        directory = ROOT / figure_directory if figure_directory else ROOT / "assets/images" / slug
        matches = sorted(directory.glob(f"figure-{figure_number:02d}.*"))
        if len(matches) != 1:
            raise ValueError(f"Expected one existing figure: {slug}/{figure_number}")
        src = "../../" + matches[0].relative_to(ROOT).as_posix()
        return f'<figure><img src="{src}" alt="{html.escape(block.get("alt", ""), quote=True)}"><figcaption>{html.escape(block.get("caption", ""))}</figcaption></figure>'
    tag = block["tag"]
    if tag not in {"p", "h2", "h3", "h4", "ul", "ol", "pre", "blockquote"}:
        raise ValueError(f"Unsupported tag: {tag}")
    # Retain semantic content/links, not Medium's styling or tracking query.
    markup = re.sub(r' class="[^"]*"', '', block["html"])
    markup = re.sub(r'\?utm_source=chatgpt\.com', '', markup)
    if re.search(r'<(?:script|iframe)|\bon\w+\s*=', markup, re.I):
        raise ValueError("Unsafe archived HTML")
    return f"<{tag}>{markup}</{tag}>"


STYLE = """body{margin:0;color:#111827;background:#fff;font:18px/1.65 system-ui,sans-serif}main{max-width:1020px;margin:auto;padding:40px 28px}h1{font-size:42px;line-height:1.15}h2{font-size:29px;line-height:1.3;color:#113e79;margin-top:46px}h3{font-size:23px}p,li{max-width:850px}a{color:#075cbd}figure{margin:35px 0}img{max-width:100%;height:auto}figcaption{font-size:15px;color:#465369}pre{background:#f3f7fd;border:1px solid #c7d8ee;padding:22px;overflow:auto;font-size:15px;line-height:1.5;white-space:pre}blockquote{border-left:4px solid #2672cb;margin:26px 0;padding:0 20px}.review{background:#f3f7fd;border:1px solid #adc7e7;padding:22px;margin-bottom:35px;font-size:16px}.review h2{margin-top:0;font-size:22px}.review pre{white-space:pre-wrap}footer{border-top:1px solid #ccd8e5;margin-top:40px;font-size:16px}"""


def main():
    reconciliation = json.loads((PACKAGE / "reconciliation-N02-N04.json").read_text())
    manifest = json.loads((PACKAGE / "manifest.json").read_text())
    settings_path = PACKAGE / "approval-N02-N04.json"
    settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    report = {"mode": "local_preparation_only", "nativeLinkedInVerified": False, "editions": []}
    for edition in manifest["editions"]:
        eid = edition["id"]
        if eid not in {"N02", "N03", "N04"}:
            continue
        slug = edition["slug"]
        archive = json.loads((ROOT / "data" / f"{slug}.json").read_text())
        rules = reconciliation[eid]
        blocks = reconcile(archive, rules)
        source_text = norm(" ".join(block_text(b, rules["figureTextInSource"]) for b in blocks))
        source_ok = (fnv(source_text) == rules["sourceHash"] and len(source_text) == rules["sourceCharacters"] and len(blocks) == rules["sourceBlocks"])
        config = settings.get(eid, {})
        proposed = copy.deepcopy(blocks)
        changes = []
        for change in config.get("replacements", []):
            idx = find_anchor(proposed, change["before"])
            proposed[idx] = text_block(change.get("tag", proposed[idx]["tag"]), change["after"])
            if change.get("html"):
                proposed[idx]["html"] = change["html"]
            changes.append(change)
        for addition in reversed(config.get("openingNotes", [])):
            proposed.insert(1, text_block("p", addition))
        if config.get("repairIllustrativeJSON"):
            found = 0
            for idx, block in enumerate(proposed):
                text = block.get("text", "")
                if text.startswith("```json"):
                    value = text.removeprefix("```json").strip().removesuffix("```").strip()
                    value = value.replace("“", '"').replace("”", '"')
                    parsed = json.loads(value)
                    proposed[idx] = text_block("pre", json.dumps(parsed, indent=2, ensure_ascii=False))
                    found += 1
            if found != 1:
                raise ValueError("Expected exactly one illustrative JSON repair")
        # Optional semantic repairs retain words; smart quote JSON repair is explicit in config.
        if config.get("repairPlaintextLists"):
            for idx, block in enumerate(proposed):
                if block.get("type") != "html" or block.get("tag") != "p":
                    continue
                text = block.get("text", "")
                if text.startswith("• "):
                    items = [x.strip() for x in re.split(r"(?:^|\n)•\s*", text) if x.strip()]
                    proposed[idx] = {"type":"html","tag":"ul","text":" ".join(items),"html":"".join(f"<li>{html.escape(x)}</li>" for x in items)}
                elif text.startswith("1. Identity:"):
                    items = [x.strip() for x in re.split(r"(?:^|\n)\d+\.\s*", text) if x.strip()]
                    proposed[idx] = {"type":"html","tag":"ol","text":" ".join(items),"html":"".join(f"<li>{html.escape(x)}</li>" for x in items)}
        chunks = []
        figure_number = 0
        for block in proposed:
            figure_number += block["type"] == "figure"
            chunks.append(render_block(block, slug, figure_number, config.get("figureDirectory")))
        body = "\n".join(chunks)
        intro = config.get("feedIntroduction", "NOT YET PREPARED")
        notes = "".join(f"<li>{html.escape(x)}</li>" for x in config.get("reviewNotes", []))
        responsive = '*{box-sizing:border-box}main{overflow-wrap:anywhere}pre{max-width:100%;overflow-wrap:normal}li{margin:8px 0}@media(max-width:600px){main{padding:22px 18px}h1{font-size:33px}h2{font-size:25px}.review{padding:18px}}'
        document = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(edition["title"])} — review</title><style>{STYLE}{responsive}</style><main><aside class="review"><h2>{eid} · Exact approval preview · Not scheduled</h2><p>Destination: The Operating AI Ledger · Newsletter edition, not standalone article.</p><p>Proposed: {html.escape(config.get("scheduleLabel", "NOT SET"))} · Anyone + Subscribers · Comments on · No mentions/hashtags · Existing first figure as cover.</p><ul>{notes}</ul><p>Exact announcement:</p><pre>{html.escape(intro)}</pre><p>This review panel is not part of the edition.</p></aside><article><h1>{html.escape(edition["title"])}</h1><section id="edition-body">{body}</section><footer>Originally published on Medium: <a href="{edition["mediumUrl"]}">{html.escape(edition["title"])}</a>.</footer></article></main></html>'''
        path = PACKAGE / f"{eid}-{slug}.html"
        path.write_text(document)
        item = {"id":eid,"sourceFidelityPassed":source_ok,"sourceFNV1a32":fnv(source_text),"expectedFNV1a32":rules["sourceHash"],"sourceCharacters":len(source_text),"sourceBlocks":len(blocks),"figures":figure_number,"sourceListCount":len(rules["lists"]),"restoredCodeBlocks":sum(x["tag"]=="pre" for x in rules.get("insertions",[])),"preview":str(path.relative_to(ROOT)),"previewSHA256":hashlib.sha256(document.encode()).hexdigest(),"proposedChanges":len(changes),"nativeRenderingVerified":False}
        item["openingNotes"] = len(config.get("openingNotes", []))
        item["proposedListCount"] = sum(b.get("tag") in {"ul", "ol"} for b in proposed)
        item["plainTextListsRepaired"] = bool(config.get("repairPlaintextLists"))
        item["illustrativeJSONRepaired"] = bool(config.get("repairIllustrativeJSON"))
        item["media"] = []
        for src in re.findall(r'<img src="([^"]+)"', document):
            media_path = (PACKAGE / src).resolve()
            item["media"].append({"path":str(media_path.relative_to(ROOT)),"sha256":hashlib.sha256(media_path.read_bytes()).hexdigest()})
        report["editions"].append(item)
        print(json.dumps(item, ensure_ascii=False))
    (PACKAGE / "validation-N02-N04.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    if not all(x["sourceFidelityPassed"] for x in report["editions"]):
        raise SystemExit("Live-source fidelity mismatch; editions MUST NOT be published.")


if __name__ == "__main__":
    main()
