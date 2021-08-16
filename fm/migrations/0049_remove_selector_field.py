# ----------------------------------------------------------------------
# Remove Selector field from Objectnotification, Commandsnippet models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
from pymongo import UpdateMany, UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [
        ("sa", "0218_command_snippet_obj_notification_resource_group"),
        ("fm", "0048_resource_group"),
    ]

    def migrate(self):
        # MAP Resource Group to Selector by name
        rg_coll = self.mongo_db["resourcegroups"]
        rg_name = {}
        for rg in rg_coll.find():
            rg_name[rg["name"]] = str(rg["_id"])
        selector_rg_map = {}
        for s_id, name in self.db.execute("SELECT id, name FROM sa_managedobjectselector"):
            name = f"MOS {name}"
            if name not in rg_name:
                continue
            selector_rg_map[s_id] = rg_name[name]
        # EventTrigger, AlarmTrigger
        for table in ("fm_eventtrigger", "fm_alarmtrigger"):
            for (s_id,) in self.db.execute(f"SELECT DISTINCT(selector_id) FROM {table}"):
                if not s_id:
                    continue
                # Append to resource groups AS services
                self.db.execute(
                    f"UPDATE {table} SET resource_group = %s WHERE selector_id = %s",
                    [selector_rg_map[s_id], s_id],
                )
            # Set profile as not null
            # self.db.execute(f"ALTER TABLE {table} ALTER resource_group SET NOT NULL")
            # Delete column
            self.db.delete_column(
                table,
                "selector_id",
            )
        # AlarmDiagnosticConfig
        ad_coll = self.mongo_db["noc.alarmdiagnosticconfig"]
        bulk = []
        for ad in ad_coll.find({"selector": {"$exists": True}}):
            if ad["selector"] not in selector_rg_map:
                continue
            bulk += [
                UpdateOne(
                    {"_id": ad["_id"]},
                    {"$set": {"resource_group": bson.ObjectId(selector_rg_map[ad["selector"]])}},
                ),
                UpdateOne(
                    {"_id": ad["_id"]},
                    {"$unset": {"selector": 1}},
                ),
            ]
        if bulk:
            ad_coll.bulk_write(bulk)
        # AlarmDiagnosticConfig
        ec_coll = self.mongo_db["noc.alarmescalatons"]
        bulk = []
        for ec in ec_coll.find({"escalations.selector": {"$exists": True}}):
            for ecc in ec.get("escalations", []):
                if "selector" in ecc and ecc["selector"] in selector_rg_map:
                    bulk += [
                        UpdateMany(
                            {
                                "_id": ec["_id"],
                                "escalations": {"$elemMatch": {"selector": ecc["selector"]}},
                            },
                            {
                                "$set": {
                                    "escalations.$.resource_group": bson.ObjectId(
                                        selector_rg_map[ecc["selector"]]
                                    )
                                }
                            },
                        ),
                        UpdateMany(
                            {
                                "_id": ec["_id"],
                                "escalations": {"$elemMatch": {"selector": ecc["selector"]}},
                            },
                            {"$unset": {"escalations.$.selector": 1}},
                        ),
                    ]
        if bulk:
            ec_coll.bulk_write(bulk)
