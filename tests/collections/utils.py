# ----------------------------------------------------------------------
# Collection test utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from collections import defaultdict

# Third-party modules
import ujson
import pytest


class CollectionTestHelper(object):
    COLLECTIONS = "collections"

    def __init__(self, model):
        self.model = model
        self.collection = model._meta["json_collection"]
        self.cache = None
        self._params = []
        self._uuid_count = defaultdict(int)
        self._name_count = defaultdict(int)

    def _iter_params(self):
        for root, _, files in os.walk(os.path.join(self.COLLECTIONS, self.collection)):
            for f in files:
                if not f.endswith(".json"):
                    continue
                yield os.path.join(root, f)

    def get_fixture_params(self):
        if not self._params:
            self._params = sorted(self._iter_params())
        return self._params

    @classmethod
    def fixture_id(cls, path):
        return os.path.join(*path.split(os.path.sep)[2:])

    def get_object(self, path):
        with open(path) as f:
            data = ujson.load(f)
            self._uuid_count[data["uuid"]] += 1
            self._name_count[data["name"]] += 1
        if self.cache is None:
            # Fill cache
            self.cache = {str(o.uuid): o for o in self.model.objects.all()}
        try:
            return self.cache[data["uuid"]]
        except KeyError:
            pytest.fail(
                "Failed to get object. Pair %s/'%s' is not unique" % (data["uuid"], data["name"])
            )

    def get_uuid_count(self, uuid):
        return self._uuid_count[str(uuid)]

    def get_name_count(self, name):
        return self._name_count[str(name)]

    def teardown(self):
        self.cache = None
        self._params = []
        self._uuid_count = defaultdict(int)
        self._name_count = defaultdict(int)
