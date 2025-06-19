# ----------------------------------------------------------------------
# Move Escalation TT field to log
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        bulk = []
        coll = self.mongo_db["noc.alarms.active"]
        for aa in coll.find(
            {
                "$or": [
                    {"escalation_tt": {"$exists": True}},
                    {"clear_notification_group": {"$exists": True}},
                ]
            },
        ):
            r = []
            log = None
            if aa.get("escalation_tt"):
                r += [
                    {
                        "effect": "tt_system",
                        "key": aa["escalation_tt"],
                        "once": True,
                        "immediate": True,
                        "clear_only": True,
                        "args": {"template": str(aa["clear_template"])}
                        if aa.get("clear_template")
                        else {},
                    }
                ]
                log = {
                    "timestamp": aa["escalation_ts"],
                    "from_status": "A",
                    "to_status": "A",
                    "message": "Escalated (migration)",
                    "tt_id": aa["escalation_tt"],
                }
            if aa.get("clear_notification_group"):
                r += [
                    {
                        "effect": "notification_group",
                        "key": aa["clear_notification_group"],
                        "once": True,
                        "immediate": True,
                        "clear_only": True,
                        "args": {"template": str(aa["clear_template"])}
                        if aa.get("clear_template")
                        else {},
                    }
                ]
            if r and log:
                bulk += [
                    UpdateOne({"_id": aa["_id"]}, {"$set": {"watchers": r}, "$push": {"log": log}})
                ]
            elif r:
                bulk += [UpdateOne({"_id": aa["_id"]}, {"$set": {"watchers": r}})]
        if bulk:
            coll.bulk_write(bulk)
        coll.update_many(
            {
                "$unset": {
                    "escalation_ts": 1,
                    "escalation_tt": 1,
                    "escalation_error": 1,
                    "clear_template": 1,
                    "clear_notification_group": 1,
                }
            }
        )
