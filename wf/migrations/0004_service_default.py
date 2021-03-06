# ----------------------------------------------------------------------
# Service Default workflow
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
                "_id": ObjectId("606eafb1d179a5da7e340a3f"),
                "name": "Service Default",
                "is_active": True,
                "description": "Service Default workflow",
                "bi_id": 5471814991222323294,
            }
        )
        # State
        db["states"].insert_many(
            [
                {
                    "_id": ObjectId("606eb05fd179a5da7e340a4f"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Closed",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 240,
                    "y": 730,
                    "bi_id": 8380089309615940674,
                    "description": "",
                },
                {
                    "_id": ObjectId("606eb01dd179a5da7e340a43"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Planned",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 240,
                    "y": 50,
                    "bi_id": 1667626383288029673,
                    "description": "The service is scheduled to be configured",
                },
                {
                    "_id": ObjectId("606eb02ed179a5da7e340a45"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Provisioning",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 240,
                    "y": 170,
                    "bi_id": 395216111673100856,
                    "description": "The service is saved to the configuration.",
                },
                {
                    "_id": ObjectId("607169bb554f2010744c3a60"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Provisioning Failed",
                    "description": "Service configuration error",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 90,
                    "y": 170,
                    "bi_id": 1819234770833760149,
                },
                {
                    "_id": ObjectId("606eb041d179a5da7e340a49"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Ready",
                    "is_default": False,
                    "is_productive": True,
                    "update_last_seen": True,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 240,
                    "y": 410,
                    "bi_id": 1171318539115933701,
                    "description": "Service is in productive usage",
                },
                {
                    "_id": ObjectId("606eb055d179a5da7e340a4d"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Removing",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 240,
                    "y": 620,
                    "bi_id": 7323723884202290227,
                    "description": "Service is removed from configuration use",
                },
                {
                    "_id": ObjectId("6071e418e3af70887f78d27a"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Removing Failed",
                    "description": "Service removing failed",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 90,
                    "y": 550,
                    "bi_id": 8473938649393578153,
                },
                {
                    "_id": ObjectId("606eb04ed179a5da7e340a4b"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Suspended",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 370,
                    "y": 520,
                    "bi_id": 941534937473202366,
                    "description": "Service is temporary suspended/blocked for organisational reasons",
                },
                {
                    "_id": ObjectId("606eb035d179a5da7e340a47"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Testing",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": True,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 240,
                    "y": 290,
                    "bi_id": 5417954856343524520,
                    "description": "Checking the service configuration",
                },
                {
                    "_id": ObjectId("606eaffbd179a5da7e340a41"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "name": "Unknown",
                    "is_default": True,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 50,
                    "y": 50,
                    "bi_id": 732593082124972534,
                    "description": "Undefined state of the service",
                },
            ]
        )
        # Transitions
        db["transitions"].insert_many(
            [
                {
                    "_id": ObjectId("6071523bd55207f22bf4b44c"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb041d179a5da7e340a49"),
                    "to_state": ObjectId("606eb04ed179a5da7e340a4b"),
                    "is_active": True,
                    "event": "suspend",
                    "label": "Suspend",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 3471543641155941751,
                    "description": "",
                },
                {
                    "_id": ObjectId("6071524f516375b6b527af4f"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb04ed179a5da7e340a4b"),
                    "to_state": ObjectId("606eb041d179a5da7e340a49"),
                    "is_active": True,
                    "event": "resume",
                    "label": "Resume",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 1438201151839821699,
                    "description": "",
                },
                {
                    "_id": ObjectId("607153a8516375b6b527af51"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb035d179a5da7e340a47"),
                    "to_state": ObjectId("606eb041d179a5da7e340a49"),
                    "is_active": True,
                    "label": "Approve",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 1604724588717964191,
                    "description": "",
                },
                {
                    "_id": ObjectId("60715720516375b6b527af53"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb01dd179a5da7e340a43"),
                    "to_state": ObjectId("606eb02ed179a5da7e340a45"),
                    "is_active": True,
                    "label": "Deploy",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 6992411654457936165,
                    "description": "",
                },
                {
                    "_id": ObjectId("60715755516375b6b527af55"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb02ed179a5da7e340a45"),
                    "to_state": ObjectId("606eb035d179a5da7e340a47"),
                    "is_active": True,
                    "label": "Check",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 2635841525332586998,
                    "description": "",
                },
                {
                    "_id": ObjectId("60715783d55207f22bf4b44e"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb04ed179a5da7e340a4b"),
                    "to_state": ObjectId("606eb055d179a5da7e340a4d"),
                    "is_active": True,
                    "label": "Remove",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 1540328197781918454,
                    "description": "",
                },
                {
                    "_id": ObjectId("60715794d55207f22bf4b450"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb055d179a5da7e340a4d"),
                    "to_state": ObjectId("606eb05fd179a5da7e340a4f"),
                    "is_active": True,
                    "label": "Close",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 8285922265787176674,
                    "description": "",
                },
                {
                    "_id": ObjectId("607157bed55207f22bf4b452"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eaffbd179a5da7e340a41"),
                    "to_state": ObjectId("606eb01dd179a5da7e340a43"),
                    "is_active": True,
                    "label": "Plan",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 6767346548535942781,
                    "description": "",
                },
                {
                    "_id": ObjectId("6071ac81e3af70887f78d276"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb035d179a5da7e340a47"),
                    "to_state": ObjectId("607169bb554f2010744c3a60"),
                    "is_active": True,
                    "label": "Fail",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 5022707057542265120,
                    "description": "",
                },
                {
                    "_id": ObjectId("6071ac98e3af70887f78d278"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("607169bb554f2010744c3a60"),
                    "to_state": ObjectId("606eb02ed179a5da7e340a45"),
                    "is_active": True,
                    "label": "Fix",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 4185271440905452741,
                    "description": "",
                },
                {
                    "_id": ObjectId("6071acb6554f2010744c3a62"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("606eb055d179a5da7e340a4d"),
                    "to_state": ObjectId("6071e418e3af70887f78d27a"),
                    "is_active": True,
                    "label": "Fail",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 6007353386252584628,
                    "description": "",
                },
                {
                    "_id": ObjectId("6071e464e3af70887f78d27c"),
                    "workflow": ObjectId("606eafb1d179a5da7e340a3f"),
                    "from_state": ObjectId("6071e418e3af70887f78d27a"),
                    "to_state": ObjectId("606eb055d179a5da7e340a4d"),
                    "is_active": True,
                    "label": "Fix",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 8998253696159292582,
                    "description": "",
                },
            ]
        )
