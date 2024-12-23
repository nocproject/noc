# ----------------------------------------------------------------------
# Agent Peer Default workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import uuid
from bson import ObjectId

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Workflow
        db["workflows"].insert_one(
            {
                "_id": ObjectId("676509728db9f670c21e14d4"),
                "name": "BGP Peer Default",
                "is_active": True,
                "uuid": uuid.UUID("dd960b97-80ac-47c0-940f-1992547b3559"),
                "description": "Workflow for BGP Peer admin status",
                "bi_id": "7520623496367707741",
            }
        )
        # State
        db["states"].insert_many(
            [
                {
                    "_id": ObjectId("67650ae68db9f670c21e14d8"),
                    "workflow": ObjectId("676509728db9f670c21e14d4"),
                    "name": "Active",
                    "uuid": uuid.UUID("e276c879-b001-435d-97b2-31f0181dad31"),
                    "description": "BGP Peer on Active working state",
                    "is_default": True,
                    "is_productive": True,
                    "is_wiping": False,
                    "hide_with_state": False,
                    "update_last_seen": True,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 150,
                    "y": 230,
                    "disable_all_interaction": False,
                    "interaction_settings": {},
                    "labels": [],
                    "bi_id": 3160973066013285039,
                },
                {
                    "_id": ObjectId("67650d328db9f670c21e14e0"),
                    "workflow": ObjectId("676509728db9f670c21e14d4"),
                    "name": "Missed",
                    "uuid": uuid.UUID("afedbc45-7b5e-4f37-8f1f-15469510aeee"),
                    "description": "BGP Peer is missed",
                    "is_default": False,
                    "is_productive": False,
                    "is_wiping": False,
                    "hide_with_state": False,
                    "update_last_seen": False,
                    "ttl": 3600,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 280,
                    "y": 310,
                    "disable_all_interaction": True,
                    "interaction_settings": {},
                    "labels": [],
                    "bi_id": 3795902531438466329,
                },
                {
                    "_id": ObjectId("67650a398db9f670c21e14d6"),
                    "workflow": ObjectId("676509728db9f670c21e14d4"),
                    "name": "Planned",
                    "uuid": uuid.UUID("6c5a3699-084d-4354-9b1c-ea119b6c8022"),
                    "description": "The BGP Peer is scheduled to be configured",
                    "is_default": False,
                    "is_productive": False,
                    "is_wiping": False,
                    "hide_with_state": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 460,
                    "y": 230,
                    "disable_all_interaction": False,
                    "interaction_settings": {},
                    "labels": [],
                    "bi_id": 3758892150013762910,
                },
                {
                    "_id": ObjectId("67650b5ad65c734a17bc0471"),
                    "workflow": ObjectId("676509728db9f670c21e14d4"),
                    "name": "Provisioning",
                    "uuid": uuid.UUID("f79d3d7a-97e1-4aab-bcf7-5c9fe3df0e56"),
                    "description": "The BGP State is saved to the configuration.",
                    "is_default": False,
                    "is_productive": False,
                    "is_wiping": False,
                    "hide_with_state": False,
                    "update_last_seen": False,
                    "ttl": 0,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 250,
                    "y": 140,
                    "disable_all_interaction": False,
                    "interaction_settings": {},
                    "labels": [],
                    "bi_id": 3930396074991330283,
                },
                {
                    "_id": ObjectId("67650a73d65c734a17bc046f"),
                    "workflow": ObjectId("676509728db9f670c21e14d4"),
                    "name": "Shutdown",
                    "uuid": uuid.UUID("e005a9ba-820a-47d2-9f1a-31301311c20e"),
                    "is_default": False,
                    "is_productive": False,
                    "is_wiping": False,
                    "hide_with_state": False,
                    "update_last_seen": False,
                    "ttl": 3600,
                    "update_expired": False,
                    "on_enter_handlers": [],
                    "on_leave_handlers": [],
                    "x": 30,
                    "y": 180,
                    "disable_all_interaction": True,
                    "interaction_settings": {},
                    "labels": [],
                    "bi_id": 1421713150115666256,
                    "description": "",
                },
            ]
        )
