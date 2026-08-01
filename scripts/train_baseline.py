#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.training import train_baseline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the TF-IDF bug-routing baseline."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=REPOSITORY_ROOT / "data" / "demo_bug_reports.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPOSITORY_ROOT / "saved_models" / "tfidf_model",
    )
    args = parser.parse_args()
    metadata = train_baseline(args.data, args.output)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
