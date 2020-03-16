# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Collection test utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

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
        return self.cache[data["uuid"]]
