# ----------------------------------------------------------------------
# docs test fixtures
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import yaml
from collections.abc import Iterable
from pathlib import Path

# Third-party modules
import pytest

DOCS_DIR = Path("docs")
SUMMARY_FILENAME = "SUMMARY.md"
MKDOCS_CONF = Path("mkdocs.yml")
rx_item = re.compile(r"\[(.*)].*\((.*)\)")

T_NAV_ITEM = str | dict[str, "T_NAV_ITEM"] | list["T_NAV_ITEM"]


class ToC:
    def __init__(self, path: Path) -> None:
        self.items: dict[tuple[str, ...], str] = {}
        for kv in self.iter_nav(path):
            self.add_item([], kv)

    @staticmethod
    def iter_nav(path: Path) -> Iterable[T_NAV_ITEM]:
        with path.open() as fp:
            data = yaml.safe_load(fp.read().replace("!!python/name:", ""))
        yield from data["nav"]

    @staticmethod
    def iter_summary(path: str) -> Iterable[tuple[str, str]]:
        if path[-1] == "/":
            path = path[:-1]
        pp = DOCS_DIR / path / SUMMARY_FILENAME
        if not pp.exists():
            return
        with open(pp, encoding="utf-8") as f:
            data = f.read().splitlines()
        for line in data:
            line = line.strip()
            if not line:
                continue
            match = rx_item.search(line)
            if match:
                yield match.group(1, 2)

    def add_item(self, path: list[str], item: T_NAV_ITEM) -> None:
        if isinstance(item, str):
            k = item
            v = item
        else:
            k = next(iter(item.keys()))
            v = item[k]
        if isinstance(v, list):
            for lkv in v:
                self.add_item([*path, k], lkv)
        else:
            self.items[(*path, k)] = v
            s_path = DOCS_DIR / v
            if s_path.is_dir():
                summary = [{sk: v + sv} for sk, sv in self.iter_summary(v)]
                if summary:
                    self.add_item(path, {k: summary})

    def __contains__(self, item: Iterable[str]) -> bool:
        return tuple(item) in self.items

    def __getitem__(self, item: Iterable[str]) -> str:
        return self.items[tuple(item)]


@pytest.fixture(scope="session")
def toc():
    return ToC(MKDOCS_CONF)
