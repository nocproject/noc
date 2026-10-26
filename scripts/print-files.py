#!/usr/bin/env python3
# ----------------------------------------------------------------------
# print-files script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

"""Print all files and directories specified by arguments."""

# Python modules
import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

HEADER_LEN = 72
NO_NEWLINE_MARKER = r"\ No newline at end of file"  # backslash is to match git output
SAFE_SUFFIXES = {
    ".py",
    ".sql",
    ".ts",
    ".json",
    ".yaml",
    ".js",
    ".conf",
    ".yml",
    ".css",
    ".sh",
    ".toml",
    ".md",
    ".html",
    ".xml",
    ".txt",
    ".j2",
}


def iter_files(paths: Iterable[str], exclude: Iterable[str]) -> Iterable[Path]:
    def is_safe(path: Path) -> bool:
        return path.is_file() and path.suffix in SAFE_SUFFIXES

    def is_excluded(path: Path) -> bool:
        return any(path == exclude or exclude in path.parents for exclude in excludes)

    excludes = tuple(Path(p) for p in exclude if p)
    for arg in paths:
        path = Path(arg)
        if is_excluded(path):
            continue
        if path.is_dir():
            for p in path.rglob("*"):
                if is_excluded(p):
                    continue
                if is_safe(p):
                    yield p
        elif is_safe(path):
            yield path


def main(*args: str) -> None:
    parser = argparse.ArgumentParser(
        description="Print all files and directories specified by arguments.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="files and directories to print",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="relative file or directory path to exclude; may be specified multiple times",
    )
    options = parser.parse_args(args)

    paths = options.paths or (".",)
    for path in iter_files(paths, exclude=options.exclude):
        header = f"===[ File: {path} ]"
        if len(header) < HEADER_LEN:
            header += "=" * (HEADER_LEN - len(header))
        content = path.read_text()
        has_trailing_newline = content.endswith("\n")
        print(header)
        print(content, end="")
        print()
        if not has_trailing_newline:
            print(NO_NEWLINE_MARKER)


if __name__ == "__main__":
    main(*sys.argv[1:])
