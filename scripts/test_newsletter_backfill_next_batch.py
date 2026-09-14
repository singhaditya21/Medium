#!/usr/bin/env python3
"""Offline fidelity/structure tests; not a claim of native or production validation."""
import ast
import hashlib
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from build_newsletter_backfill_batch import ROOT, PACKAGE, plain
from build_newsletter_backfill_next_batch import build


class Page(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.images = []
        self.links = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))


class NextBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.report = json.loads((PACKAGE / 'validation-N05-N07.json').read_text())
        cls.approval = json.loads((PACKAGE / 'approval-N05-N07.json').read_text())

    def test_all_sources_match_live_fingerprint(self):
        self.assertEqual([e['id'] for e in self.report['editions']], ['N05', 'N06', 'N07'])
        self.assertTrue(all(e['liveSourceTextMatches'] for e in self.report['editions']))

    def test_images_and_local_links_exist(self):
        counts = []
        for edition in self.report['editions']:
            path = ROOT / edition['preview']
            page = Page(path.read_text())
            counts.append(len(page.images))
            for image in page.images:
                self.assertTrue(image.get('alt'))
                self.assertTrue((path.parent / image['src']).resolve().is_file())
            for link in page.links:
                if link.startswith('../../'):
                    self.assertTrue((path.parent / link).resolve().is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), edition['previewSha256'])
        self.assertEqual(counts, [30, 18, 18])

    def test_every_original_code_block_renders_unchanged(self):
        counts = []
        for edition in self.report['editions']:
            preview = (ROOT / edition['preview']).read_text()
            slug = Path(edition['preview']).stem[4:]
            archive = json.loads((ROOT / 'data' / f'{slug}.json').read_text())
            source = [b['text'] for b in archive['blocks'] if b.get('tag') == 'pre']
            body = preview.split('<article id="edition-body">')[1].split('</article>')[0]
            rendered = re.findall(r'<pre>(.*?)</pre>', body, re.S)
            self.assertEqual([plain(p) for p in rendered], source)
            counts.append(len(rendered))
            for code in source:
                if code.strip().startswith('{'):
                    json.loads(code)
                if code.startswith('def '):
                    ast.parse(code)
        self.assertEqual(counts, [0, 15, 9])

    def test_no_public_action_or_secret_surface(self):
        self.assertEqual(self.approval['state'], 'awaiting_exact_action_time_approval')
        self.assertFalse(self.report['nativeSchedulingVerified'])
        self.assertEqual(self.approval['settings']['mentions'], [])
        for edition in self.report['editions']:
            page = (ROOT / edition['preview']).read_text()
            self.assertNotRegex(page, r'<(?:script|iframe)|\bon\w+\s*=')
            self.assertNotRegex(page, r'/article/edit/|medium\.com/p/[^/]+/edit|ghp_[A-Za-z0-9]{16,}|sk-proj-[A-Za-z0-9]{16,}')
            self.assertIn('not scheduled', page)
            self.assertIn('AI writing and visualization assistance', page)

    def test_weekly_dates_are_only_proposals(self):
        from datetime import datetime, timedelta
        dates = [datetime.fromisoformat(self.approval[eid]['scheduleISO']) for eid in ['N05','N06','N07']]
        self.assertEqual([d.weekday() for d in dates], [0,0,0])
        self.assertEqual(dates[1]-dates[0], timedelta(days=7))
        self.assertEqual(dates[2]-dates[1], timedelta(days=7))
        self.assertFalse(self.approval['settings']['nativeSchedulingVerified'])

    def test_illustrative_arithmetic(self):
        self.assertEqual(2400000 * .12, 288000)
        self.assertAlmostEqual(.25*.82+.25*.75+.20*.88+.15*.92+.15*1-.35*.20, .7865)

    def test_checkpoints_are_provisional_and_uncollected(self):
        from datetime import datetime, timedelta
        plan = json.loads((PACKAGE / 'newsletter-checkpoints.json').read_text())
        self.assertEqual(plan['mode'], 'review_plan_only_no_scheduler_registered')
        self.assertEqual(len(plan['editions']), 4)
        for row in plan['editions']:
            anchor = datetime.fromisoformat(row['anchor'].replace('Z', '+00:00'))
            self.assertEqual([c['hours'] for c in row['checkpoints']], [48,168,672])
            for checkpoint in row['checkpoints']:
                self.assertEqual(datetime.fromisoformat(checkpoint['dueAt']) - anchor, timedelta(hours=checkpoint['hours']))
                self.assertIsNone(checkpoint['collectedAt'])
                self.assertIsNone(checkpoint['editionViews'])


if __name__ == '__main__':
    unittest.main()
