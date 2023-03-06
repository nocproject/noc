#!/usr/bin/env python
# ----------------------------------------------------------------------
# Convert black output to junit xml
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
from typing import Iterable
from dataclasses import dataclass
from xml.sax.saxutils import escape


@dataclass
class Item(object):
    path: str
    text: str


def iter_problems() -> Iterable[Item]:
    section = []
    for line in sys.stdin:
        if line.startswith("+++"):
            section = []
            continue
        if line.startswith("would reformat "):
            yield Item(path=line[15:].strip(), text="".join(section))
            section = []
            continue
        section.append(line)


def main() -> int:
    problems = list(iter_problems())
    r = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<testsuite errors="0" failures="{len(problems)}" '
        f'name="black" skipped="0" tests="{len(problems)}" time="0.0">',
    ]
    for item in problems:
        r += [
            f'  <testcase classname="black" file="{escape(item.path)}" line="1" '
            f'name="black" '
            'time="0.0">',
            f"    <failure>{escape(item.text)}</failure>",
            "  </testcase>",
        ]
    r.append("</testsuite>")
    print("\n".join(r))
    if problems:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
