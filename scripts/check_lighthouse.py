#!/usr/bin/env python3
"""Fail when a Lighthouse report is below the repository quality thresholds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


THRESHOLDS = {"performance": 0.75, "accessibility": 0.90, "best-practices": 0.85, "seo": 0.90}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+", type=Path)
    args = parser.parse_args()
    failures = []
    for report in args.reports:
        payload = json.loads(report.read_text(encoding="utf-8"))
        scores = payload.get("categories", {})
        print(report)
        for category, minimum in THRESHOLDS.items():
            score = scores.get(category, {}).get("score")
            print(f"  {category}: {score if score is not None else 'missing'} (minimum {minimum})")
            if score is None or score < minimum:
                failures.append(f"{report}: {category}={score}, expected >= {minimum}")
    if failures:
        raise SystemExit("Lighthouse thresholds failed:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    main()
