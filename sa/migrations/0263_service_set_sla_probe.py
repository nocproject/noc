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

BULK = 1000


class Migration(BaseMigration):
    def migrate(self):
        svc = self.mongo_db["noc.services"]
        bulk = []
        # SLA Probes
        for row in self.mongo_db["noc.sla_probes"].find(
            {"service": {"$ne": None, "$exists": True}}, {"service": 1}
        ):
            bulk.append(UpdateOne({"_id": row["service"]}, {"$set": {"sla_probe": row["_id"]}}))
            if len(bulk) > BULK:
                svc.bulk_write(bulk)
                bulk = []
        if bulk:
            svc.bulk_write(bulk)
        self.mongo_db["noc.sla_probes"].update_many({}, {"$unset": {"service": 1}})
