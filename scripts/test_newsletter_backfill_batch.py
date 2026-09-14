"""Regression tests for the local-only newsletter review builder."""
import json
from pathlib import Path
import re
import unittest

import build_newsletter_backfill_batch as builder


class NewsletterReviewTests(unittest.TestCase):
    def test_complete_source_fingerprints(self):
        rules = json.loads((builder.PACKAGE / "reconciliation-N02-N04.json").read_text())
        manifest = json.loads((builder.PACKAGE / "manifest.json").read_text())
        for edition in manifest["editions"]:
            if edition["id"] not in {"N02", "N03", "N04"}:
                continue
            rule = rules[edition["id"]]
            archive = json.loads((builder.ROOT / "data" / f'{edition["slug"]}.json').read_text())
            blocks = builder.reconcile(archive, rule)
            text = builder.norm(" ".join(builder.block_text(b, rule["figureTextInSource"]) for b in blocks))
            with self.subTest(edition=edition["id"]):
                self.assertEqual(builder.fnv(text), rule["sourceHash"])
                self.assertEqual(len(text), rule["sourceCharacters"])
                self.assertEqual(len(blocks), rule["sourceBlocks"])

    def test_ambiguous_and_missing_anchors_fail_closed(self):
        blocks = [builder.text_block("p", "same"), builder.text_block("p", "same")]
        with self.assertRaises(ValueError):
            builder.find_anchor(blocks, "same")
        with self.assertRaises(ValueError):
            builder.find_anchor(blocks, "missing")
        self.assertEqual(builder.find_anchor(blocks, "same", occurrence=1), 0)

    def test_html_visible_text_matches_declared_text(self):
        config = json.loads((builder.PACKAGE / "approval-N02-N04.json").read_text())
        for eid in ("N02", "N03", "N04"):
            for change in config[eid]["replacements"]:
                if change.get("html"):
                    self.assertEqual(builder.norm(builder.plain(change["html"])), builder.norm(change["after"]))

    def test_all_local_media_exist_and_have_alt(self):
        for page in builder.PACKAGE.glob("N0[234]-*.html"):
            document = page.read_text()
            for src, alt in re.findall(r'<img src="([^"]+)" alt="([^"]*)">', document):
                self.assertTrue((page.parent / src).resolve().is_file(), src)
                self.assertTrue(alt)
            self.assertNotIn("<script", document.lower())
            self.assertNotIn("linkedin.com/article/edit/", document)

    def test_code_json_remains_structured(self):
        for page in builder.PACKAGE.glob("N0[34]-*.html"):
            document = page.read_text().split('<section id="edition-body">', 1)[1]
            count = 0
            for snippet in re.findall(r"<pre>(.*?)</pre>", document, re.S):
                text = builder.plain(snippet)
                if text.startswith("{"):
                    self.assertIsInstance(json.loads(text), dict)
                    count += 1
            self.assertEqual(count, 3 if page.name.startswith("N03") else 1)

    def test_publication_remains_unapproved(self):
        config = json.loads((builder.PACKAGE / "approval-N02-N04.json").read_text())
        self.assertEqual(config["state"], "awaiting_exact_action_time_approval")
        self.assertFalse(config["settings"]["nativeSchedulingVerified"])
        self.assertEqual(config["publicationType"], "newsletter_edition")
        self.assertEqual(config["N02"]["scheduleISO"], "2026-09-21T14:00:00+05:30")
        self.assertEqual(config["N03"]["scheduleISO"], "2026-09-28T14:00:00+05:30")
        self.assertEqual(config["N04"]["scheduleISO"], "2026-10-05T14:00:00+05:30")


if __name__ == "__main__":
    unittest.main()
