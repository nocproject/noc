# ----------------------------------------------------------------------
# ManagedObject Default workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from bson import ObjectId, Int64

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Workflow
        db["workflows"].insert_one(
            {
                "_id": ObjectId("641b35e6fa01fd032a1f61ef"),
                "name": "ManagedObject Default",
                "is_active": True,
                "description": "ManagedObject Default Workflow",
                "bi_id": Int64("2858828191196989734"),
            }
        )
        # State
        db["states"].insert_many(
            [
                {
                    "_id": ObjectId("641b35e6fa01fd032a1f61f1"),
                    "workflow": ObjectId("641b35e6fa01fd032a1f61ef"),
                    "name": "Managed",
                    "is_default": True,
                    "is_productive": True,
                    "update_last_seen": True,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 280,
                    "y": 360,
                    "labels": [],
                    "effective_labels": [],
                    "bi_id": Int64("2667556019038926839"),
                },
                {
                    "_id": ObjectId("641b371eb846e3cc661ea8b5"),
                    "workflow": ObjectId("641b35e6fa01fd032a1f61ef"),
                    "name": "Not Managed",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 3600,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 410,
                    "y": 200,
                    "effective_labels": [],
                    "bi_id": Int64("478291320657225258"),
                    "disable_all_interaction": True
                },
                {
                    "_id": ObjectId("641b371eb846e3cc661ea8b3"),
                    "workflow": ObjectId("641b35e6fa01fd032a1f61ef"),
                    "name": "Removing",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 3600,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 540,
                    "y": 460,
                    "labels": [],
                    "effective_labels": [],
                    "bi_id": Int64("5174969568830998645"),
                    "is_wiping": True,
                    "description": ""
                }

            ]
        )
        # Transitions
        db["transitions"].insert_many(
            [
                {
                    "_id": ObjectId("641b371eb846e3cc661ea8b9"),
                    "workflow": ObjectId("641b35e6fa01fd032a1f61ef"),
                    "from_state": ObjectId("641b35e6fa01fd032a1f61f1"),
                    "to_state": ObjectId("641b371eb846e3cc661ea8b3"),
                    "is_active": True,
                    "event": "remove",
                    "label": "Remove",
                    "description": "",
                    "enable_manual": True,
                    "handlers": [],
                    "required_rules": [],
                    "vertices": [
                        {
                            "x": 390,
                            "y": 480
                        }
                    ],
                    "bi_id": Int64("6196188485054338054")
                },
                {
                    "_id": ObjectId("641b371eb846e3cc661ea8bb"),
                    "workflow": ObjectId("641b35e6fa01fd032a1f61ef"),
                    "from_state": ObjectId("641b371eb846e3cc661ea8b5"),
                    "to_state": ObjectId("641b371eb846e3cc661ea8b3"),
                    "is_active": True,
                    "event": "expired",
                    "label": "Remove",
                    "enable_manual": True,
                    "handlers": [],
                    "required_rules": [],
                    "vertices": [],
                    "bi_id": Int64("8882898918256034369"),
                    "description": ""
                },
                {
                    "_id": ObjectId("641b3c5e219a478783321716"),
                    "workflow": ObjectId("641b35e6fa01fd032a1f61ef"),
                    "from_state": ObjectId("641b371eb846e3cc661ea8b5"),
                    "to_state": ObjectId("641b35e6fa01fd032a1f61f1"),
                    "is_active": True,
                    "event": "managed",
                    "label": "Managed",
                    "enable_manual": True,
                    "handlers": [],
                    "required_rules": [],
                    "vertices": [
                        {
                            "x": 350,
                            "y": 220
                        }
                    ],
                    "bi_id": Int64("7512540641524375121")
                },
                {
                    "_id": ObjectId("641b3c5e219a47878332171a"),
                    "workflow": ObjectId("641b35e6fa01fd032a1f61ef"),
                    "from_state": ObjectId("641b35e6fa01fd032a1f61f1"),
                    "to_state": ObjectId("641b371eb846e3cc661ea8b5"),
                    "is_active": True,
                    "event": "unmanaged",
                    "label": "Unmanaged",
                    "enable_manual": True,
                    "handlers": [],
                    "required_rules": [],
                    "vertices": [],
                    "bi_id": Int64("7078692477969553649")
                }
            ]
        )
