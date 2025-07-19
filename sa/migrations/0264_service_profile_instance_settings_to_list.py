# ---------------------------------------------------------------------
# Migrate SLA Probe service to Service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        bulk = []
        coll = self.mongo_db["noc.serviceprofiles"]
        # SLA Probes
        for row in coll.find(
            {"instance_policy_settings": {"$ne": None, "$exists": True}},
            {"instance_policy_settings": 1},
        ):
            bulk.append(
                UpdateOne(
                    {"_id": row["_id"]},
                    {"$set": {"instance_settings": [row["instance_policy_settings"]]}},
                )
            )
        if bulk:
            coll.bulk_write(bulk)
        # self.mongo_db["noc.sla_probes"].update_many({}, {"$unset": {"service": 1}})
