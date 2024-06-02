#!/usr/bin/env python
# ----------------------------------------------------------------------
# Convert black output to junit xml
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import sys
from dataclasses import dataclass
import os
from typing import Iterable, Optional
from xml.sax.saxutils import escape


@dataclass
class Item(object):
    path: str
    text: str


def iter_problems(tee: bool = False) -> Iterable[Item]:
    section = []
    for line in sys.stdin:
        if tee:
            sys.stdout.write(line)
        if line.startswith("+++"):
            section = []
            continue
        if line.startswith("would reformat "):
            yield Item(path=line[15:].strip(), text="".join(section))
            section = []
            continue
        section.append(line)


def process(out: Optional[str] = None, tee: bool = False) -> int:
    problems = list(iter_problems(tee))
    r = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<testsuite errors="0" failures="{len(problems)}" '
        f'name="black" skipped="0" tests="{len(problems)}" time="0.0">',
    ]
    for item in problems:
        cls_name = item.path.replace(os.sep, ".")[:-3]
        r += [
            f'  <testcase classname="black.{cls_name}" file="{escape(item.path)}" line="1" '
            f'name="black: {item.path}" '
            'time="0.0">',
            f"    <failure>{escape(item.text)}</failure>",
            "  </testcase>",
        ]
    r.append("</testsuite>")
    if problems:
        if out:
            with open(out, "w") as f:
                f.write("\n".join(r))
        else:
            sys.stdout.write("\n".join(r))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="black-junit.py", description="Format black output to JUnit XML"
    )
    parser.add_argument("-t", "--tee", dest="tee", action="store_true")
    parser.add_argument("-o", "--output", dest="output")
    args = parser.parse_args()
    return process(out=args.output, tee=args.tee)


if __name__ == "__main__":
    sys.exit(main())
