# ----------------------------------------------------------------------
# ReportObjectLinkCount datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.core.mongo.connection import get_db
from .base import BaseReportColumn


class ReportObjectLinkCount(BaseReportColumn):
    """Report for MO link count"""

    name = "link_count"
    unknown_value = (0,)
    builtin_sorted = True

    def extract(self):
        sync_ids_set = set(self.sync_ids)
        value = (
            get_db()["noc.links"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$unwind": "$interfaces"},
                    {
                        "$lookup": {
                            "from": "noc.interfaces",
                            "localField": "interfaces",
                            "foreignField": "_id",
                            "as": "int",
                        }
                    },
                    # {"$match": {"int.managed_object": {"$in": self.sync_ids}}},
                    {"$group": {"_id": "$int.managed_object", "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}},
                ],
                allowDiskUse=True,
            )
        )
        for v in value:
            if not v["_id"] or v["_id"][0] not in sync_ids_set:
                continue
            yield v["_id"][0], v["count"]
