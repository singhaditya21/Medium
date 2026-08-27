#!/usr/bin/env python3
"""Render a LinkedIn execution receipt as an auditable GitHub issue comment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


LABELS = {
    "comment_posted": "LinkedIn comment posted",
    "reply_posted": "LinkedIn reply posted",
    "author_comment_posted": "LinkedIn author comment posted",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    result = receipt["result"]
    operation_id = receipt["operationId"]
    print(f"<!-- linkedin-execution:{operation_id} -->")
    print(f"### {LABELS[receipt['action']]}")
    print()
    print(f"- Candidate: `{result['candidateId']}`")
    print(f"- Target: {result['targetUrl']}")
    print(f"- Verified public result: {result['publicUrl']}")
    print(f"- Approved-text SHA-256: `{result['publishedTextSha256']}`")
    print(f"- Verified at: {result['verifiedAt']}")
    print(f"- Verification: {result['verification']}")
    print("- GitHub Actions performed LinkedIn action: no")


if __name__ == "__main__":
    main()
