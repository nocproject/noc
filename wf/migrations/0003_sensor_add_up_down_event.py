# ----------------------------------------------------------------------
# Sensor Add event for Fixed and Non-operational signals
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from bson import ObjectId
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.mongo_db["transitions"].bulk_write(
            [
                # Non-operational
                UpdateOne(
                    {
                        "_id": ObjectId("5fca627e890f55564231e1ff"),
                    },
                    {"$set": {"event": "down"}},
                ),
                # Fixed
                UpdateOne({"_id": ObjectId("5fca627e890f55564231e205")}, {"$set": {"event": "up"}}),
            ]
        )
