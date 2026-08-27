# LinkedIn execution receipts

This directory contains credential-free receipts created only after one individually approved action has been completed and visibly verified in the user's signed-in LinkedIn session.

GitHub Actions validates these receipts; it never creates them as proof of a LinkedIn action. A receipt binds the candidate, exact target, public result URL, and SHA-256 digest of the approved text without storing passwords, cookies, browser storage, or session data.

Supported actions are `comment_posted`, `reply_posted`, and `author_comment_posted`. Record them with `scripts/record_linkedin_execution.py`.
