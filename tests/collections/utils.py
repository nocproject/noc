# -*- coding: utf-8 -*-
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


class CollectionTestHelper(object):
    COLLECTIONS = "collections"

    def __init__(self, model):
        self.model = model
        self.collection = model._meta["json_collection"]
        self.cache = None
        self._params = []
        self._ids = []
        self._uuid_count = defaultdict(int)

    def _init_fixture_params(self):
        for root, _, files in os.walk(os.path.join(self.COLLECTIONS, self.collection)):
            for f in files:
                if not f.endswith(".json"):
                    continue
                path = os.path.join(root, f)
                self._params += [path]
                self._ids += [os.path.join(*path.split(os.path.sep)[2:])]

    def get_fixture_params(self):
        if not self._params:
            self._init_fixture_params()
        return self._params

    def get_fixture_ids(self):
        if not self._ids:
            self._init_fixture_params()
        return self._ids

    def get_object(self, path):
        with open(path) as f:
            data = ujson.load(f)
        if self.cache is None:
            # Fill cache
            self.cache = {}
            for obj in self.model.objects.all():
                self.cache[str(obj.uuid)] = obj
        self._uuid_count[data["uuid"]] += 1
        return self.cache[data["uuid"]]

    def get_uuid_count(self, uuid):
        return self._uuid_count[str(uuid)]

    def teardown(self):
        self.cache = None
        self._params = []
        self._ids = []
        self._uuid_count = defaultdict(int)
