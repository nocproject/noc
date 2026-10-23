# ----------------------------------------------------------------------
# ReportObjectConfig datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.core.mongo.connection import get_db
from .base import BaseReportColumn


class ReportObjectConfig(BaseReportColumn):
    """Report for MO link count"""

    name = "config_ts"
    unknown_value = (None,)
    builtin_sorted = True

    def extract(self):
        pipeline = [
            {"$group": {"_id": "$object", "last_ts": {"$max": "$ts"}}},
            {"$sort": {"_id": 1}},
        ]
        if len(self.sync_ids) < 20000:
            # @todo Very large list slowest encode, need research
            pipeline.insert(0, {"$match": {"object": {"$in": self.sync_ids}}})
        value = (
            get_db()["noc.gridvcs.config.files"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(pipeline, allowDiskUse=True)
        )
        for v in value:
            if not v["_id"]:
                continue
            yield v["_id"], v["last_ts"]
