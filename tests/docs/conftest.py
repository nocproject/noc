# ----------------------------------------------------------------------
# docs test fixtures
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import yaml


class ToC(object):
    def __init__(self, path):
        with open(path) as f:
            data = yaml.safe_load(f.read().replace("!!python/name:", ""))
        self.items = {}
        for kv in data["nav"]:
            self.add_item([], kv)

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

    def __contains__(self, item):
        return tuple(item) in self.items

    def __getitem__(self, item):
        return self.items[tuple(item)]


@pytest.fixture(scope="session")
def toc():
    return ToC("mkdocs.yml")
