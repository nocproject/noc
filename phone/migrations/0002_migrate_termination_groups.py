# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Convert TerminationGroups to ResourceGroups
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0184_managedobject_migrate_termination_groups")]

    def migrate(self):
        # Get migrated termination groups, created by 0184 migration
        db = self.mongo_db
        rg_map = {
            x["_legacy_id"]: x["_id"]
            for x in db.resourcegroups.find(
                {"_legacy_id": {"$exists": True}}, {"_id": 1, "_legacy_id": 1}
            )
        }
        # Apply Resource Groups
        for cname in ["noc.phoneranges", "noc.phonenumbers"]:
            coll = db[cname]
            bulk = []
            for d in coll.aggregate([{"$group": {"_id": "$termination_group"}}]):
                if not d.get("_id"):
                    continue
                rg_id = rg_map[d["_id"]]
                bulk += [
                    UpdateMany(
                        {"termination_group": d["_id"]},
                        {
                            "$set": {
                                "static_client_groups": [rg_id],
                                "effective_client_groups": [rg_id],
                            },
                            "$unset": {"termination_group": ""},
                        },
                    )
                ]
            if bulk:
                coll.bulk_write(bulk)
