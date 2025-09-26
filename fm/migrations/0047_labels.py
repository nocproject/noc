# ----------------------------------------------------------------------
# Migrate labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    TAG_COLLETIONS = [("noc.alarms.active", ""), ("noc.alarms.archived", "")]

    def migrate(self):
        # Mongo models
        for collection, setting in self.TAG_COLLETIONS:
            coll = self.mongo_db[collection]
            coll.bulk_write(
                [UpdateMany({"tags": {"$exists": True}}, {"$rename": {"tags": "labels"}})]
            )
        # Unset tags
        for collection, setting in self.TAG_COLLETIONS:
            coll.bulk_write([UpdateMany({}, {"$unset": {"tags": 1}})])
