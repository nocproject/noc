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
from .base import BaseReportDataSource
from noc.lib.nosql import get_db
from noc.inv.models.capability import Capability


class ReportObjectCaps(BaseReportDataSource):
    """
    Report caps for MO
    Query: db.noc.sa.objectcapabilities.aggregate([{$unwind: "$caps"},
    {$match: {"caps.source" : "caps"}},
    {$project: {key: "$caps.capability", value: "$caps.value"} },
    {$group: {"_id": "$_id", "cap": {$push: { item: "$key", quantity: "$value" } }}}])
    """
    ATTRS = dict([("c_%s" % str(key), value) for key, value in
                  Capability.objects.filter().scalar("id", "name")])
    UNKNOWN = [""] * len(ATTRS)
    CHUNK_SIZE = 10000

    def load(self, mo_ids, attributes):
        # Namedtuple caps, for save
        Caps = namedtuple("Caps", attributes.keys())
        Caps.__new__.__defaults__ = ("",) * len(Caps._fields)

        d = {}
        while mo_ids:
            mo_ids, chunk = mo_ids[:self.CHUNK_SIZE], mo_ids[self.CHUNK_SIZE:]
            match = {"_id": {"$in": chunk}}
            value = get_db()["noc.sa.objectcapabilities"].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate(
                [
                    {"$match": match},
                    {"$unwind": "$caps"},
                    {"$match": {"caps.source": "caps"}},
                    {"$project": {"key": "$caps.capability", "value": "$caps.value"}},
                    {"$group": {"_id": "$_id", "cap": {"$push": {"item": "$key", "val": "$value"}}}}
                ])

            for v in value:
                r = dict(("c_%s" % l["item"], l["val"]) for l in v["cap"] if "c_%s" % l["item"] in attributes)
                d[v["_id"]] = Caps(**r)
        return d
