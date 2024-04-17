# ----------------------------------------------------------------------
# Strict Platform name to 200
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration

MAX_PLATFORM_LENGTH = 200


class Migration(BaseMigration):
    def migrate(self):
        platform_coll = self.mongo_db["noc.platforms"]
        bulk = []
        for p in platform_coll.find({}, {"name": 1}):
            if len(p["name"]) > 200:
                bulk += [
                    UpdateOne(
                        {"_id": p["_id"]}, {"$set": {"name": p["name"][:MAX_PLATFORM_LENGTH]}}
                    )
                ]
        if bulk:
            platform_coll.bulk_write(bulk)
