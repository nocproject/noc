# ----------------------------------------------------------------------
# Normalize CPE global id MAC
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.sa.interfaces.base import MACAddressParameter


class Migration(BaseMigration):
    def migrate(self):
        cpe_coll = self.mongo_db["cpes"]
        bulk = []
        # DropIndex
        for cpe in cpe_coll.find({}, {"global_id": 1}):
            if "global_id" not in cpe:
                continue
            try:
                gid = MACAddressParameter().clean(cpe["global_id"])
            except ValueError:
                continue
            bulk += [
                UpdateOne(
                    {"_id": cpe["_id"]},
                    {
                        "$set": {
                            "global_id": gid,
                        }
                    },
                ),
            ]
            if len(bulk) > 500:
                cpe_coll.bulk_write(bulk)
                bulk = []
        if bulk:
            cpe_coll.bulk_write(bulk)
