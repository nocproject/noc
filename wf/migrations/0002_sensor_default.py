# ----------------------------------------------------------------------
# Sensor Default workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Workflow
        db["workflows"].insert_one(
            {
                "_id": ObjectId("5fca627e890f55564231e1f5"),
                "name": "Sensor Default",
                "is_active": True,
                "description": "Sensor default workflow",
                "bi_id": 9192762612914402473,
            }
        )
        # State
        db["states"].insert_many(
            [
                {
                    "_id": ObjectId("5fca627e890f55564231e1f7"),
                    "workflow": ObjectId("5fca627e890f55564231e1f5"),
                    "name": "Ok",
                    "description": "",
                    "is_default": True,
                    "is_productive": True,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 290,
                    "y": 40,
                    "bi_id": 246779251013309823,
                },
                {
                    "_id": ObjectId("5fca627e890f55564231e1fb"),
                    "workflow": ObjectId("5fca627e890f55564231e1f5"),
                    "name": "Missed",
                    "description": "Sensor is missed",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 140,
                    "y": 160,
                    "bi_id": 1925217288374048050,
                },
                {
                    "_id": ObjectId("5fca627e890f55564231e1fd"),
                    "workflow": ObjectId("5fca627e890f55564231e1f5"),
                    "name": "Non-operational",
                    "description": "Sensor is broken or non-operational",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 440,
                    "y": 150,
                    "bi_id": 6087488050439942373,
                },
            ]
        )
        # Transitions
        db["transitions"].insert_many(
            [
                {
                    "_id": ObjectId("5fca627e890f55564231e1ff"),
                    "workflow": ObjectId("5fca627e890f55564231e1f5"),
                    "from_state": ObjectId("5fca627e890f55564231e1f7"),
                    "to_state": ObjectId("5fca627e890f55564231e1fd"),
                    "is_active": True,
                    "event": "",
                    "label": "Non-operational",
                    "description": "",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [{"x": 450, "y": 60}],
                    "bi_id": 44894602916285118,
                },
                {
                    "_id": ObjectId("5fca627e890f55564231e201"),
                    "workflow": ObjectId("5fca627e890f55564231e1f5"),
                    "from_state": ObjectId("5fca627e890f55564231e1f7"),
                    "to_state": ObjectId("5fca627e890f55564231e1fb"),
                    "is_active": True,
                    "event": "missed",
                    "label": "missed",
                    "description": "",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 311387734538203880,
                },
                {
                    "_id": ObjectId("5fca627e890f55564231e203"),
                    "workflow": ObjectId("5fca627e890f55564231e1f5"),
                    "from_state": ObjectId("5fca627e890f55564231e1fb"),
                    "to_state": ObjectId("5fca627e890f55564231e1f7"),
                    "is_active": True,
                    "event": "seen",
                    "label": "Seen",
                    "description": "",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 5858192813321598962,
                },
                {
                    "_id": ObjectId("5fca627e890f55564231e205"),
                    "workflow": ObjectId("5fca627e890f55564231e1f5"),
                    "from_state": ObjectId("5fca627e890f55564231e1fd"),
                    "to_state": ObjectId("5fca627e890f55564231e1f7"),
                    "is_active": False,
                    "event": "",
                    "label": "Fixed",
                    "description": "",
                    "enable_manual": False,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 1720440267695078397,
                },
            ]
        )
