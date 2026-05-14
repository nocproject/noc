# ----------------------------------------------------------------------
# Fix duplicate list on Object part_no
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

# Third-party modules
from pymongo import UpdateOne

BULK_SIZE = 1000


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.objects"]
        bulk = []
        for row in coll.find({"data.attr": "part_no"}, {"data": 1}):
            for d in row["data"]:
                if (
                    d["attr"] == "part_no"
                    and d["value"]
                    and isinstance(d["value"], list)
                    and isinstance(d["value"][0], list)
                ):
                    d["value"] = d["value"][0]
                    bulk += [UpdateOne({"_id": row["_id"]}, {"$set": {"data": row["data"]}})]
                    break
            if len(bulk) > BULK_SIZE:
                coll.bulk_write(bulk)
                bulk = []
        if bulk:
            coll.bulk_write(bulk)
