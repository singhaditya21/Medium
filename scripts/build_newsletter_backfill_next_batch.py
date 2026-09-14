#!/usr/bin/env python3
"""Build local N05–N07 review artifacts only; no network or publishing actions."""
import copy
import hashlib
import html
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from build_newsletter_backfill_batch import ROOT, PACKAGE, STYLE, render_block, plain, norm, fnv, text_block


def canonical_source(value):
    value = value.translate(str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"', '–': '-', '—': '-', '•': '*'}))
    value = re.sub(r"\s*-\s*", "-", value)
    return norm(value)


def build():
    manifest = json.loads((PACKAGE / "manifest.json").read_text())
    config_path = PACKAGE / "approval-N05-N07.json"
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    audit_path = PACKAGE / "audit-N05-N07.json"
    audit = json.loads(audit_path.read_text()) if audit_path.exists() else {}
    report = {"mode": "local_review_only", "nativeSchedulingVerified": False, "editions": []}
    for edition in manifest["editions"]:
        eid = edition["id"]
        if eid not in {"N05", "N06", "N07"}:
            continue
        source = ROOT / "data" / f"{edition['slug']}.json"
        archive = json.loads(source.read_text())
        blocks = copy.deepcopy(archive["blocks"])
        for block in blocks:
            if block.get("tag") == "pre":
                block["html"] = html.escape(block["text"])
        rules = config.get(eid, {})
        if rules.get("subtitle"):
            blocks.insert(0, text_block("h2", rules["subtitle"]))
        for addition in rules.get("append", []):
            blocks.append(text_block(addition["tag"], addition["text"], addition.get("href")))
        source_blocks = blocks[1:] if rules.get("subtitle") else blocks
        source_text = canonical_source(' '.join(plain(b['html']) for b in source_blocks if b['type'] != 'figure'))
        expected = audit.get("sources", {}).get(eid)
        source_matches = expected is not None and fnv(source_text) == expected["fnv"] and len(source_text) == expected["characters"]
        if expected and not source_matches:
            raise ValueError(f"Source fidelity failed {eid}: {fnv(source_text)} / {len(source_text)}")
        # Preserve the source text; only convert unambiguous line-separated lists.
        for block in blocks:
            if block.get("tag") != "p":
                continue
            lines = block.get("html", "").split("<br>")
            if len(lines) < 2:
                continue
            marker = r"^\s*(?:[•*]|\d+[.])\s+"
            if all(re.match(marker, plain(line)) for line in lines):
                ordered = bool(re.match(r"^\s*\d+[.]", plain(lines[0])))
                items = []
                for line in lines:
                    # Some archives wrap each marker in strong tags.
                    line = re.sub(r"^\s*<strong>(?:[•*]|\d+[.])</strong>\s*", "", line)
                    line = re.sub(marker, "", line)
                    items.append(f"<li>{line}</li>")
                block["tag"] = "ol" if ordered else "ul"
                block["html"] = ''.join(items)
        count = 0
        rendered = []
        figures = []
        for block in blocks:
            if block["type"] == "figure":
                count += 1
                paths = list((ROOT / "assets/images" / edition["slug"]).glob(f"figure-{count:02d}.*"))
                assert len(paths) == 1
                figures.append({"path": paths[0].relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(paths[0].read_bytes()).hexdigest()})
            markup = render_block(block, edition["slug"], count)
            if block["type"] == "figure":
                image_src = '../../' + figures[-1]["path"]
                markup = markup.replace('<img ', f'<a href="{image_src}" title="Open full-resolution figure"><img ', 1).replace('><figcaption>', '></a><figcaption>', 1)
            rendered.append(markup)
        preview = PACKAGE / f"{eid}-{edition['slug']}.html"
        review = f'<aside class="review"><h2>Review only — not scheduled</h2><p>The Operating AI Ledger · {html.escape(rules.get("scheduleLabel", "Date pending"))} · Anyone + Subscribers · Comments on · Standard newsletter notifications</p><p>Existing first figure as cover. No mentions, hashtags, additional attachments or separate messages. Medium and all existing schedules remain unchanged.</p><h3>Exact feed introduction</h3><pre>{html.escape(rules.get("feedIntroduction", "Pending source QA"))}</pre><h3>Review notes</h3><ul>'
        review += ''.join(f'<li>{html.escape(note)}</li>' for note in rules.get("reviewNotes", ["Archive-based working preview. Live reconciliation pending."])) + '</ul></aside>'
        notes = ''.join(f'<p>{html.escape(note)}</p>' for note in rules.get("openingNotes", []))
        page = f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(edition["title"])}</title><style>{STYLE}@media(max-width:600px){{main{{padding:24px 16px}}h1{{font-size:33px}}}}</style><main>{review}<h1>{html.escape(edition["title"])}</h1><section id="republication-notes">{notes}</section><article id="edition-body">' + '\n'.join(rendered) + f'</article><footer>Source: <a href="{edition["mediumUrl"]}">Published Medium story</a>. Republication in The Operating AI Ledger.</footer></main></html>'
        preview.write_text(page)
        report["editions"].append({"id": eid, "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(), "preview": preview.relative_to(ROOT).as_posix(), "previewSha256": hashlib.sha256(preview.read_bytes()).hexdigest(), "blocks": len(blocks), "figures": figures, "sourceTextCharacters": len(source_text), "sourceTextFNV": fnv(source_text), "liveSourceTextMatches": source_matches, "nativeVerified": False})
    (PACKAGE / "validation-N05-N07.json").write_text(json.dumps(report, indent=2) + '\n')
    approval_lines = [
        '# Exact approval — N05–N07 newsletter editions',
        '',
        '**Prepared locally; not created or scheduled on LinkedIn.**',
        '',
        'Destination: [The Operating AI Ledger](' + config['destination'] + '), Aditya Singh. Three full newsletter editions, not three new newsletters or standalone articles.',
        '',
        'Settings for all: Anyone + Subscribers; comments On; standard LinkedIn newsletter notifications; existing figure 1 as cover and all inline source figures retained. No mentions, hashtags, separate DMs, additional feed posts or new animation. No Medium edits, canonical changes, paywall changes or schedule changes are bundled. Actual email delivery is not guaranteed.',
        '',
        'The exact publishable content in each preview is its title, republication note (where present), full article body and linked source footer. The blue review box is NOT part of the edition; its feed introduction is the exact announcement text. Click a figure to inspect its full resolution. Native formatting/media/settings must be checked before scheduling; stop for approval if a material change is needed.',
        '',
    ]
    for edition in report['editions']:
        eid = edition['id']
        row = next(e for e in manifest['editions'] if e['id'] == eid)
        rules = config[eid]
        approval_lines += [f'## {eid} — {row["title"]}', '', f'Proposed time: **{rules["scheduleLabel"]}**. [Complete exact preview]({Path(edition["preview"]).name}). {len(edition["figures"])} inline figures.', '', 'Exact feed introduction:', '']
        approval_lines += ['> ' + line if line else '>' for line in rules['feedIntroduction'].split('\n')]
        approval_lines += ['', 'Review notes:', ''] + ['- ' + note for note in rules['reviewNotes']]
        if rules.get('openingNotes'):
            approval_lines += ['', 'Exact new republication note included in the article:', ''] + ['> ' + note for note in rules['openingNotes']]
        approval_lines += ['', f'Frozen preview SHA-256: `{edition["previewSha256"]}`.', '']
    approval_lines += ['## Separate optional timing-only approval: T1 and T2', '', 'The live audit found two exact collisions. Proposed changes:', '', '- **T1:** “A 97% approval rate can coexist with a broken approval system.” Move its ordinary feed post from September 21, 2026 at 14:00 IST to September 22 at 08:45 IST.', '- **T2:** “A memory system can achieve 104 ms p95 retrieval and still be unsafe.” Move its ordinary feed post from October 5, 2026 at 14:00 IST to October 6 at 08:45 IST.', '', 'For both, preserve every other setting, text, mention, link and existing video. Do not move N02 or N04. N05–N07 approval does not imply T1/T2 approval.', '', 'Reply with the IDs you approve and “exactly as previewed/listed.” All inventories and duplicate checks will be refreshed immediately before execution.', '', 'See [audit and future plan](future-execution-plan.md) for coverage, source checks, remaining backfills, the 20-story pipeline and validation limits.', '']
    (PACKAGE / 'approval-N05-N07.md').write_text('\n'.join(approval_lines))
    receipt = json.loads((PACKAGE / 'execution-N01.json').read_text())
    checkpoints = {'mode': 'review_plan_only_no_scheduler_registered', 'metricsCollected': False, 'editions': []}
    for row in manifest['editions'][:4]:
        eid = row['id']
        anchor = receipt['recordedAt'] if eid == 'N01' else row['scheduledFor']
        date = datetime.fromisoformat(anchor.replace('Z', '+00:00'))
        checkpoints['editions'].append({'id': eid, 'title': row['title'], 'anchor': anchor,
            'anchorType': 'publication_observation_proxy' if eid == 'N01' else 'scheduled_release_requires_public_verification',
            'publicEditionUrl': row.get('linkedInEditionUrl'),
            'checkpoints': [{'hours': h, 'dueAt': (date+timedelta(hours=h)).isoformat(), 'collectedAt': None,
                'seriesSubscribers': None, 'editionViews': None, 'availableReadingMetric': None,
                'announcementImpressions': None, 'announcementComments': None,
                'mediumPresentations': None, 'mediumViews': None, 'mediumReads': None} for h in [48,168,672]]})
    (PACKAGE / 'newsletter-checkpoints.json').write_text(json.dumps(checkpoints, indent=2)+'\n')
    print(json.dumps({"mode": report["mode"], "editions": [{"id": e["id"], "blocks": e["blocks"], "figures": len(e["figures"])} for e in report["editions"]]}, indent=2))


if __name__ == '__main__':
    build()
