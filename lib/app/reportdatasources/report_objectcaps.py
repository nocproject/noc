# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectHostname datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import namedtuple
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportColumn
from noc.lib.nosql import get_db
from noc.inv.models.capability import Capability


class ReportObjectCaps(BaseReportColumn):
    """
    Report caps for MO
    Query: db.noc.sa.objectcapabilities.aggregate([{$unwind: "$caps"},
    {$match: {"caps.source" : "caps"}},
    {$project: {key: "$caps.capability", value: "$caps.value"} },
    {$group: {"_id": "$_id", "cap": {$push: { item: "$key", quantity: "$value" } }}}])
    """
    builtin_sorted = True

    ATTRS = dict([("c_%s" % str(key), value) for key, value in
                  Capability.objects.filter().scalar("id", "name")])
    unknown_value = ([""] * len(ATTRS), )
    CHUNK_SIZE = 10000

    def extract(self):
        # load(self, mo_ids, attributes):
        # Namedtuple caps, for save
        Caps = namedtuple("Caps", self.ATTRS.keys())
        Caps.__new__.__defaults__ = ("",) * len(Caps._fields)

        mo_ids = self.sync_ids[:]
        while mo_ids:
            chunk, mo_ids = mo_ids[:self.CHUNK_SIZE], mo_ids[self.CHUNK_SIZE:]
            match = {"_id": {"$in": chunk}}
            value = get_db()["noc.sa.objectcapabilities"].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate(
                [
                    {"$match": match},
                    {"$unwind": "$caps"},
                    {"$match": {"caps.source": "caps"}},
                    {"$project": {"key": "$caps.capability", "value": "$caps.value"}},
                    {"$group": {"_id": "$_id", "cap": {"$push": {"item": "$key", "val": "$value"}}}},
                    {"$sort": {"_id": 1}},
                ])
            for v in value:
                r = dict(("c_%s" % l["item"], l["val"]) for l in v["cap"] if "c_%s" % l["item"] in self.ATTRS)
                yield v["_id"], Caps(**r)
