# ----------------------------------------------------------------------
# Delete MX routes for notification type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import DeleteMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        mr_coll = self.mongo_db["messageroutes"]
        cfg_coll = self.mongo_db["ds_cfgmxroute"]
        routes = []
        for r in mr_coll.find({"type": "notification"}, {"_id": 1}):
            routes.append(r["_id"])
        if routes:
            mr_coll.bulk_write([DeleteMany({"_id": {"$in": routes}})])
            cfg_coll.bulk_write([DeleteMany({"_id": {"$in": [str(r) for r in routes]}})])
