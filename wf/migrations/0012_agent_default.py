# ----------------------------------------------------------------------
# Agent Default workflow
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
                "_id": ObjectId("610bcff0902971a3863306fb"),
                "name": "Agent Default",
                "is_active": True,
                "description": "Agent Default Workflow",
                "bi_id": 3468966898630074545,
            }
        )
        # State
        db["states"].insert_many(
            [
                {
                    "_id": ObjectId("610be4c771b6da38e5f5acb2"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "name": "Approved",
                    "description": "Agent is approved for ready",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 260,
                    "y": 50,
                    "labels": ["noc::agent::auth::pre"],
                    "effective_labels": ["noc::agent::auth::pre"],
                    "bi_id": 3373553393116727828,
                },
                {
                    "_id": ObjectId("610be3c671b6da38e5f5acb0"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "name": "New",
                    "description": "New registered agent on System",
                    "is_default": True,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 50,
                    "y": 50,
                    "labels": ["noc::agent::auth::none"],
                    "effective_labels": ["noc::agent::auth::none"],
                    "bi_id": 6693212396144621794,
                },
                {
                    "_id": ObjectId("610bd09371b6da38e5f5acae"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "name": "Ready",
                    "description": "Agent is in productive usage",
                    "is_default": False,
                    "is_productive": True,
                    "update_last_seen": True,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 260,
                    "y": 200,
                    "labels": ["noc::agent::auth::auth"],
                    "effective_labels": ["noc::agent::auth::auth"],
                    "bi_id": 6323558026723790432,
                },
                {
                    "_id": ObjectId("610be4fd902971a3863306ff"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "name": "Removing",
                    "description": "Agent is removed from system use",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 350,
                    "y": 370,
                    "labels": ["noc::agent::auth::none"],
                    "effective_labels": ["noc::agent::auth::none"],
                    "bi_id": 5644536921567111119,
                },
                {
                    "_id": ObjectId("610be4d9902971a3863306fd"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "name": "Suspended",
                    "description": "Agent is temporary suspended/blocked for organisational reasons",
                    "is_default": False,
                    "is_productive": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 140,
                    "y": 300,
                    "labels": ["noc::agent::auth::pre"],
                    "effective_labels": ["noc::agent::auth::pre"],
                    "bi_id": 7418372945801511030,
                },
            ]
        )
        # Transitions
        db["transitions"].insert_many(
            [
                {
                    "_id": ObjectId("610be699902971a386330701"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "from_state": ObjectId("610be4c771b6da38e5f5acb2"),
                    "to_state": ObjectId("610bd09371b6da38e5f5acae"),
                    "is_active": True,
                    "event": "seen",
                    "label": "Seen",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 2789875778847456366,
                    "description": "",
                },
                {
                    "_id": ObjectId("610be6b471b6da38e5f5acb5"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "from_state": ObjectId("610bd09371b6da38e5f5acae"),
                    "to_state": ObjectId("610be4d9902971a3863306fd"),
                    "is_active": True,
                    "event": "suspend",
                    "label": "Suspend",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 7385490058000949812,
                    "description": "",
                },
                {
                    "_id": ObjectId("610be6c771b6da38e5f5acb7"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "from_state": ObjectId("610be4d9902971a3863306fd"),
                    "to_state": ObjectId("610bd09371b6da38e5f5acae"),
                    "is_active": True,
                    "event": "resume",
                    "label": "Resume",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 3738440408351158595,
                    "description": "",
                },
                {
                    "_id": ObjectId("610be6f871b6da38e5f5acb9"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "from_state": ObjectId("610be4d9902971a3863306fd"),
                    "to_state": ObjectId("610be4fd902971a3863306ff"),
                    "is_active": True,
                    "label": "Remove",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 6195769163155286672,
                    "description": "",
                },
                {
                    "_id": ObjectId("610be76671b6da38e5f5acbb"),
                    "workflow": ObjectId("610bcff0902971a3863306fb"),
                    "from_state": ObjectId("610be3c671b6da38e5f5acb0"),
                    "to_state": ObjectId("610be4c771b6da38e5f5acb2"),
                    "is_active": True,
                    "event": "approve",
                    "label": "Approve",
                    "enable_manual": True,
                    "handlers": [],
                    "vertices": [],
                    "bi_id": 8807158971147672185,
                    "description": "",
                },
            ]
        )
        db["labels"].insert_many(
            [
                {
                    # "_id": bson.ObjectId(),
                    "name": label,
                    "description": descr,
                    "bg_color1": 10181046,
                    "fg_color1": 16777215,
                    "bg_color2": 3447003,
                    "fg_color2": 16777215,
                    "is_protected": True,
                    # Label scope
                    "enable_agent": True,
                    "enable_service": False,
                    "enable_serviceprofile": False,
                    "enable_managedobject": False,
                    "enable_managedobjectprofile": False,
                    "enable_administrativedomain": False,
                    "enable_authprofile": False,
                    "enable_commandsnippet": False,
                    "enable_workflowstate": True,
                    # Exposition scope
                    "expose_metric": False,
                    "expose_datastream": False,
                }
                for label, descr in [
                    ("noc::agent::*", "Agent authentication precessed labels"),
                    ("noc::agent::auth::none", "Agent is not authenticate and "),
                    (
                        "noc::agent::auth::pre",
                        "Agent is registration on system and wait approve for authentication",
                    ),
                    (
                        "noc::agent::auth::auth",
                        "Agent is authenticate and allow getting collector config",
                    ),
                ]
            ]
        )
