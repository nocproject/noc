# ----------------------------------------------------------------------
# ReportObjectHostname datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.core.mongo.connection import get_db
from noc.inv.models.capability import Capability
from .base import BaseReportColumn


class ReportObjectCaps(BaseReportColumn):
    """
    Report caps for MO
    Query: db.noc.sa.objectcapabilities.aggregate([{$unwind: "$caps"},
    {$match: {"caps.source" : "caps"}},
    {$project: {key: "$caps.capability", value: "$caps.value"} },
    {$group: {"_id": "$_id", "cap": {$push: { item: "$key", quantity: "$value" } }}}])
    """

    builtin_sorted = True

    ATTRS = {
        "c_%s" % str(key): value
        for key, value in Capability.objects.filter().order_by("name").scalar("id", "name")
    }
    unknown_value = ([""] * len(ATTRS),)
    CHUNK_SIZE = 10000

    def extract(self):
        # load(self, mo_ids, attributes):
        # Namedtuple caps, for save
        Caps = namedtuple("Caps", list(self.ATTRS))
        Caps.__new__.__defaults__ = ("",) * len(Caps._fields)

        mo_ids = self.sync_ids[:]
        while mo_ids:
            chunk, mo_ids = mo_ids[: self.CHUNK_SIZE], mo_ids[self.CHUNK_SIZE :]
            match = {"_id": {"$in": chunk}}
            value = (
                get_db()["noc.sa.objectcapabilities"]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(
                    [
                        {"$match": match},
                        {"$unwind": "$caps"},
                        {"$match": {"caps.source": {"$in": ["caps", "manual"]}}},
                        {"$project": {"key": "$caps.capability", "value": "$caps.value"}},
                        {
                            "$group": {
                                "_id": "$_id",
                                "cap": {"$push": {"item": "$key", "val": "$value"}},
                            }
                        },
                        {"$sort": {"_id": 1}},
                    ]
                )
            )
            for v in value:
                r = {
                    f"c_{ll['item']}": ll["val"]
                    for ll in v["cap"]
                    if f"c_{ll['item']}" in self.ATTRS
                }
                yield v["_id"], Caps(**r)
