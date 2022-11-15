# ----------------------------------------------------------------------
# ReportObjectIfacesTypeStat datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import BaseReportColumn
from noc.core.mongo.connection import get_db


class ReportObjectIfacesTypeStat(BaseReportColumn):
    """Report for MO interfaces count"""

    name = "ifacestypestat"
    unknown_value = (0,)
    builtin_sorted = True

    def extract(self):
        i_type = "physical"
        match = {"type": i_type}
        if len(self.sync_ids) < 20000:
            # @todo Very large list slowest encode, need research
            match = {"type": i_type, "managed_object": {"$in": self.sync_ids}}
        value = (
            get_db()["noc.interfaces"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$match": match},
                    {"$group": {"_id": "$managed_object", "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}},
                ],
                allowDiskUse=True,
            )
        )
        for v in value:
            if not v["_id"]:
                continue
            yield v["_id"], v["count"]
