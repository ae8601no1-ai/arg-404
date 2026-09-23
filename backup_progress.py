"""Create a consistent backup of the ARG progress SQLite database."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get("ARG_DB_PATH") or ROOT / ".local/progress.sqlite3")
DEST_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".local/backups"


def main() -> int:
    if not SOURCE.exists():
        print(f"Database not found: {SOURCE}", file=sys.stderr)
        return 1

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = DEST_DIR / f"progress-{stamp}.sqlite3"

    with sqlite3.connect(SOURCE) as src, sqlite3.connect(dest) as out:
        src.backup(out)

    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
