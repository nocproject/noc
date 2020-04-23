# ---------------------------------------------------------------------
# Move InterfaceProfile.mac_discovery to .mac_discovery_policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        coll = db["noc.interface_profiles"]
        for d in list(coll.find({}, {"_id": 1, "mac_discovery": 1})):
            coll.update_many(
                {"_id": d["_id"]},
                {
                    "$set": {"mac_discovery_policy": "e" if d.get("mac_discovery") else "d"},
                    "$unset": {"mac_discovery": 1},
                },
            )
