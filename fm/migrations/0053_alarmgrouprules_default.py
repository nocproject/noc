# ----------------------------------------------------------------------
# Alarm Group Default
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from bson import ObjectId
import uuid

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Alarm Class
        db["noc.alarmclasses"].insert_one(
            {
                "_id": ObjectId("6172add005d0668829888eae"),
                "name": "Group",
                "uuid": uuid.UUID("4644ca2a-4cfc-4818-9467-49d7e57cb47d"),
                "description": "Default Alarm Class for grouping alarms",
                "is_unique": False,
                "is_ephemeral": True,
                "reference": [],
                "user_clearable": False,
                "datasources": [],
                "components": [],
                "vars": [
                    {"name": "name", "description": "Alarm Group name"},
                ],
                "subject_template": "Group Alarm {{alarm.vars.name}}",
                "body_template": "Group Alarm",
                "recommended_actions": "Ignore this",
                "flap_condition": "none",
                "flap_window": 0,
                "flap_threshold": 0,
                "root_cause": [],
                "topology_rca": False,
                "handlers": [],
                "clear_handlers": [],
                "plugins": [],
                "recover_time": 0,
                "bi_id": 6432359933583168679,
                "category": ObjectId("6172adba835d62a6f337f55e"),
            }
        )
        # Alarm Group Rule
        db["alarmrules"].insert_one(
            {
                "_id": ObjectId("6172a2c994b882e61820692b"),
                "name": "default",
                "is_active": True,
                "description": "Default Alarm Group",
                "match": [],
                "groups": [
                    {
                        "reference_template": "",
                        "alarm_class": ObjectId("6172add005d0668829888eae"),
                        "title_template": "",
                    }
                ],
                "actions": [],
                "bi_id": 8422126749852039790,
            }
        )
