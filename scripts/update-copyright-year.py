#!/usr/bin/env python3
# ----------------------------------------------------------------------
# Update copyright year
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

"""
Update copyright year in modified git files.

Looks for lines like:

    # Copyright (C) 2007-2026

and replaces the ending year with the current one.
Only Added (A) and Modified (M) files are processed.
"""

# Future imports
from __future__ import annotations

# Python modules
import datetime
import re
import subprocess
from pathlib import Path

CURRENT_YEAR = datetime.date.today().year

COPYRIGHT_RE = re.compile(r"(# Copyright \(C\) \d{4}-)(\d{4})")


def iter_changed_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(name) for name in result.stdout.splitlines() if name]


def update_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        return False

    changed = False

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        if match.group(2) == str(CURRENT_YEAR):
            return match.group(0)
        changed = True
        return f"{match.group(1)}{CURRENT_YEAR}"

    new_text = COPYRIGHT_RE.sub(repl, text)

    if changed:
        path.write_text(new_text, encoding="utf-8")
        print(f"Updated {path}")

    return changed


def main() -> None:
    updated = 0
    for path in iter_changed_files():
        if update_file(path):
            updated += 1
    print(f"Updated {updated} file(s).")


if __name__ == "__main__":
    main()
