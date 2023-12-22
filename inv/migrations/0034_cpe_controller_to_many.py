# ----------------------------------------------------------------------
# Migrate CPE.controller to controllers threshold profiles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

# Third-party modules
from pymongo import InsertOne, UpdateMany, UpdateOne


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Migrate profiles
        cpe_coll = db["noc.cpes"]
        bulk = []
        # DropIndex
        for cpe in cpe_coll.find():
            bulk += [
                UpdateOne(
                    {"_id": cpe["_id"]},
                    {
                        "$set": {
                            "controllers": {
                                "controller": cpe["controller"],
                                "local_id": cpe["local_id"],
                                "interface": cpe.get("interface"),
                                "is_active": True,
                            }
                        }
                    },
                ),
                UpdateOne(
                    {"_id": cpe["_id"]},
                    {"$unset": {"controller": 1, "local_id": 1, "interface": 1}},
                ),
            ]
            if len(bulk) > 500:
                cpe_coll.bulk_write(bulk)
                bulk = []
        if bulk:
            cpe_coll.bulk_write(bulk)
