# ----------------------------------------------------------------------
# SLAProbe Default workflow
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
                "_id": ObjectId("607a7dddff3a857a47600b9b"),
                "name": "SLAProbe Default",
                "is_active": True,
                "description": "SLAProbe Default workflow",
                "bi_id": 6074994055776808888,
            }
        )
        # State
        db["states"].insert_many(
            [
                {
                    "_id": ObjectId("607a7e25ff3a857a47600b9d"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "name": "Missed",
                    "description": "Sensor is missed",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 3600,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 250,
                    "y": 60,
                    "bi_id": 3623368907948585294,
                },
                {
                    "_id": ObjectId("607a7e2e3d18d4fb3c12032c"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "name": "Non-operational",
                    "description": "Sensor is broken or non-operational",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 520,
                    "y": 210,
                    "bi_id": 1472075281703656507,
                },
                {
                    "_id": ObjectId("607a7e1d3d18d4fb3c12032a"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "name": "Ok",
                    "is_default": True,
                    "is_productive": True,
                    "update_last_seen": True,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 390,
                    "y": 110,
                    "bi_id": 1399253602890530658,
                    "description": "",
                },
            ]
        )
        # Transitions
        db["transitions"].insert_many(
            [
                {
                    "_id": ObjectId("607a7ee0ff3a857a47600b9f"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "from_state": ObjectId("607a7e1d3d18d4fb3c12032a"),
                    "to_state": ObjectId("607a7e2e3d18d4fb3c12032c"),
                    "is_active": True,
                    "event": "down",
                    "label": "Down",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 7493433118747194768,
                    "description": "",
                },
                {
                    "_id": ObjectId("607a7efdff3a857a47600ba1"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "from_state": ObjectId("607a7e1d3d18d4fb3c12032a"),
                    "to_state": ObjectId("607a7e25ff3a857a47600b9d"),
                    "is_active": True,
                    "event": "missed",
                    "label": "Missed",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 8862543170371985128,
                },
                {
                    "_id": ObjectId("607a7f123d18d4fb3c12032e"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "from_state": ObjectId("607a7e25ff3a857a47600b9d"),
                    "to_state": ObjectId("607a7e1d3d18d4fb3c12032a"),
                    "is_active": True,
                    "event": "seen",
                    "label": "Seen",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 5922870540207143342,
                    "description": "",
                },
                {
                    "_id": ObjectId("607a7f22ff3a857a47600ba3"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "from_state": ObjectId("607a7e2e3d18d4fb3c12032c"),
                    "to_state": ObjectId("607a7e1d3d18d4fb3c12032a"),
                    "is_active": True,
                    "event": "up",
                    "label": "Up",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 2661405338408447282,
                    "description": "",
                },
                {
                    "_id": ObjectId("607a8d6c671ee0c6812ee21e"),
                    "workflow": ObjectId("607a7dddff3a857a47600b9b"),
                    "from_state": ObjectId("607a7e2e3d18d4fb3c12032c"),
                    "to_state": ObjectId("607a7e25ff3a857a47600b9d"),
                    "is_active": True,
                    "event": "missed",
                    "label": "Missed",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [{"x": 390, "y": 230}],
                    "bi_id": 5981567621944996631,
                    "description": "",
                },
            ]
        )
