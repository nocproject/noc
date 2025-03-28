# ----------------------------------------------------------------------
# docs test fixtures
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import re
from typing import List, Tuple

# Third-party modules
import pytest
import yaml

DOCS_DIR = "docs"
SUMMARY_FILENAME = "SUMMARY.md"


class ToC(object):
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f.read().replace("!!python/name:", ""))
        self.items = {}
        for kv in data["nav"]:
            self.add_item([], kv)

    @staticmethod
    def get_summary(path: str) -> List[Tuple]:
        if path[-1] == "/":
            path = path[:-1]
        pp = os.path.join(DOCS_DIR, path, SUMMARY_FILENAME)
        if os.path.exists(pp):
            result = []
            with open(pp, "r", encoding="utf-8") as f:
                data = f.read().splitlines()
            for line in data:
                if line.strip():
                    key, value = re.search(r"\[(.*)].*\((.*)\)", line).group(1, 2)
                    result += [(key, value)]
            return result
        return []

    def add_item(self, path, kv):
        if isinstance(kv, str):
            k = kv
            v = kv
        else:
            k = list(kv.keys())[0]
            v = kv[k]
        if isinstance(v, list):
            for lkv in v:
                self.add_item(path + [k], lkv)
        else:
            self.items[tuple(path + [k])] = v
            s_path = os.path.join(DOCS_DIR, v)
            if os.path.isdir(s_path):
                summary = [{sk: v + sv} for sk, sv in self.get_summary(v)]
                if summary:
                    self.add_item(path, {k: summary})

    def __contains__(self, item):
        return tuple(item) in self.items

    def __getitem__(self, item):
        return self.items[tuple(item)]


@pytest.fixture(scope="session")
def toc():
    return ToC("mkdocs.yml")
