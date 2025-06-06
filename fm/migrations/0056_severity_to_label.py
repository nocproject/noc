# ----------------------------------------------------------------------
# Migrate AlarmClass Severities to Labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import InsertOne, UpdateMany
from bson import ObjectId, Int64

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash


class Migration(BaseMigration):
    def migrate(self):
        s_coll = self.mongo_db["noc.alarmseverities"]
        l_coll = self.mongo_db["labels"]
        severity_weight_map = {}
        current_labels = {ll["name"]: ll["_id"] for ll in l_coll.find()}
        l_bulk, ac_bulk = [], []
        # Add severities labels
        for row in s_coll.find():
            severity_weight_map[row["name"].lower()] = row["_id"]
            l_name = f'noc::severity::{row["name"].lower()}'
            ac_bulk += [
                UpdateMany({"default_severity": row["_id"]}, {"$set": {"labels": [l_name]}})
            ]
            if l_name in current_labels:
                continue
            l_bulk.append(
                InsertOne(
                    {
                        "name": l_name,
                        "description": "Builtin Labels mark for Alarm Severity",
                        "bg_color1": 16777215,
                        "fg_color1": 0,
                        "bg_color2": 16777215,
                        "fg_color2": 0,
                        "is_protected": True,
                        "is_autogenerated": False,
                        "enable_alarm": True,
                    }
                )
            )
        # Replace Alarm Class Severity
        ac_coll = self.mongo_db["noc.alarmclasses"]
        if ac_bulk:
            ac_coll.bulk_write(ac_bulk)
        ac_coll.update_many({}, {"$unset": {"default_severity": 1}})
        if l_bulk:
            l_coll.bulk_write(l_bulk)
        bulk = []
        # Create AlarmRules
        for s_name, s_id in severity_weight_map.items():
            ar_id = ObjectId()
            bulk += [
                InsertOne(
                    {
                        "_id": ar_id,
                        "name": f"{s_name.upper()} Alarms",
                        "description": f"Up Alarm Severities to {s_name.upper()}",
                        "is_active": True,
                        "match": [
                            {
                                "labels": [f"noc::severity::{s_name}"],
                                "exclude_labels": [],
                                "reference_rx": "",
                            }
                        ],
                        "groups": [],
                        "actions": [
                            {
                                "when": "raise",
                                "policy": "continue",
                                "severity": s_id,
                            }
                        ],
                        "bi_id": Int64(bi_hash(ar_id)),
                    }
                )
            ]
        if bulk:
            self.mongo_db["alarmrules"].bulk_write(bulk)
