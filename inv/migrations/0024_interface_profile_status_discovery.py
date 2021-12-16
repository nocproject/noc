# ----------------------------------------------------------------------
# Migrate InterfaceProfile threshold profiles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Migrate profiles
        p_coll = db["noc.interface_profiles"]
        p_coll.update_many({"status_discovery": True}, {"$set": {"status_discovery": "e"}})
        p_coll.update_many({"status_discovery": False}, {"$set": {"status_discovery": "d"}})
