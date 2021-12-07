# ----------------------------------------------------------------------
# Migrate ActiveAlarm to Escalation document
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        bulk = []
        db = self.mongo_db
        # Alarm Class
        active_alarms = db.noc.alarms.active
        for doc in active_alarms.find(
            {
                "managed_object": {"$exists": True},
                "alarm_class": {"$exists": True},
                "escalation_tt": {"$exists": True},
            },
            {
                "managed_object": 1,
                "timestamp": 1,
                "escalation_ts": 1,
                "escalation_tt": 1,
                "escalation_error": 1,
            },
        ):
            bulk += [
                InsertOne(
                    {
                        "timestamp": doc["escalation_ts"],
                        "tt_id": doc["escalation_tt"],
                        "items": [
                            {
                                "managed_object": doc["managed_object"],
                                "alarm": doc["_id"],
                                "escalation_status": "ok",
                                "deescalation_status": "active",
                            }
                        ],
                        "groups": [],
                    }
                )
            ]
        if bulk:
            db["escalations"].bulk_write(bulk)
