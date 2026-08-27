# Signed-in execution receipts

This directory contains credential-free receipts created only after a user-initiated action has been completed and verified in the signed-in Medium UI.

GitHub Actions never creates these receipts on its own and never treats the presence of an approval issue as proof that a Medium action occurred. The signed-in operator must verify the visible result first, then record it with `scripts/record_medium_execution.py`.

Allowed receipt types:

- `draft_imported`: the exact GitHub Pages story was imported and remains a saved Medium draft;
- `draft_revised`: an explicitly approved replacement body was saved into an existing scheduled story, with its preserved settings and content verification recorded;
- `story_scheduled`: the exact story, canonical link, topics, delivery settings, and future publication time were confirmed in Medium's Scheduled tab;
- `story_published`: the exact story and final settings were confirmed, published, and verified publicly;
- `stats_captured`: a dated aggregate snapshot was read from the signed-in Stats and Audience surfaces;
- `response_posted`: one individually approved Medium response was published and its public URL verified.

Never store draft URLs, cookies, passwords, access tokens, browser storage, account email addresses, subscriber-level information, or private messages here.
