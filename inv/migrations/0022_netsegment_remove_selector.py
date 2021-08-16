# ----------------------------------------------------------------------
# Remove Selector field from NetworkSegment
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [
        ("sa", "0218_command_snippet_obj_notification_resource_group"),
    ]

    def migrate(self):
        # NetworkSegment
        ns_coll = self.mongo_db["noc.networksegments"]
        ns_coll.bulk_write(
            [
                UpdateMany(
                    {"selector": {"$exists": True}},
                    {"$unset": {"selector": 1}},
                )
            ]
        )
