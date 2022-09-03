# ----------------------------------------------------------------------
# Migrate status_change_notification reference field to string
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        l_coll = self.mongo_db["noc.interface_profiles"]
        l_coll.bulk_write(
            [
                UpdateMany(
                    {"status_change_notification": {"$exists": True}},
                    {"$set": {"status_change_notification": "e"}},
                )
            ]
        )
