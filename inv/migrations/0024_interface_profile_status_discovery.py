# ----------------------------------------------------------------------
# Migrate InterfaceProfile threshold profiles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Third-party modules
import cachetools

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    _ac_cache = cachetools.TTLCache(maxsize=5, ttl=60)

    def migrate(self):
        db = self.mongo_db
        # Migrate profiles
        p_coll = db["noc.interface_profiles"]
        for p in p_coll.find():
            if p["status_discovery"]:
                p_coll.update_one({"_id": p["_id"]}, {"$set": {"status_discovery": "e"}})
            else:
                p_coll.update_one({"_id": p["_id"]}, {"$set": {"status_discovery": "d"}})
