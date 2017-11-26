# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Default workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        # Workflow
        db["workflows"].insert({
            "_id": bson.ObjectId("5a01d980b6f529000100d37a"),
            "name": "Default Resource",
            "is_active": True,
            "bi_id": long(1099501303790147280L),
            "description": "Default resource workflow with external provisioning"
        })
        # State
        db["states"].insert([
            {
                "_id": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "name": "Free",
                "is_default": True,
                "is_productive": False,
                "update_last_seen": False,
                "ttl": 0,
                "update_expired": False,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(5784899502721162850L),
                "description": "Resource is free and can be used"
            },
            {
                "_id": bson.ObjectId("5a17f6c51bb6270001bd0333"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "name": "Reserved",
                "is_default": False,
                "is_productive": False,
                "update_last_seen": False,
                "ttl": 604800,
                "update_expired": False,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(346135885535479406L),
                "description": "Resource is temporary reserved/booked. It must be approved explicitly during TTL to became used"
            },
            {
                "_id": bson.ObjectId("5a17f7391bb6270001bd033e"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "name": "Cooldown",
                "is_default": False,
                "is_productive": False,
                "update_last_seen": False,
                "ttl": 2592000,
                "update_expired": False,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(5541827829820576149L),
                "description": "Cooldown stage for released resources to prevent reuse collisions"
            },
            {
                "_id": bson.ObjectId("5a17f78d1bb6270001bd0346"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "name": "Ready",
                "is_default": False,
                "is_productive": True,
                "update_last_seen": False,
                "ttl": 604800,
                "update_expired": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(6326503631568495692L),
                "description": "Resource is in productive usage"
            },
            {
                "_id": bson.ObjectId("5a17f7d21bb6270001bd034f"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "name": "Approved",
                "is_default": False,
                "is_productive": False,
                "update_last_seen": False,
                "ttl": 0,
                "update_expired": False,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(6239532707574720775L),
                "description": "Resource reservation is approved. Resource will became ready when it will be discovered"
            },
            {
                "_id": bson.ObjectId("5a17f7fc1bb6270001bd0359"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "name": "Suspended",
                "is_default": False,
                "is_productive": False,
                "update_last_seen": False,
                "ttl": 0,
                "update_expired": False,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(8871888520366972039L),
                "description": "Resource is temporary suspended/blocked for organisational reasons"
            }
        ])
        # Transitions
        db["transitions"].insert([
            {
                "_id": bson.ObjectId("5a1813e41bb6270001c70309"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                "to_state": bson.ObjectId("5a17f78d1bb6270001bd0346"),
                "is_active": True,
                "label": "Seen",
                "event": "seen",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(8800448533721856912L)
            },
            {
                "_id": bson.ObjectId("5a18140b1bb6270001c7031c"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                "to_state": bson.ObjectId("5a17f6c51bb6270001bd0333"),
                "is_active": True,
                "label": "Reserve",
                "event": "reserve",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(7126984897086158544L)
            },
            {
                "_id": bson.ObjectId("5a18146a1bb6270001c70332"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f6c51bb6270001bd0333"),
                "to_state": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                "is_active": True,
                "label": "Expired",
                "event": "expired",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(6910421850576189953L)
            },
            {
                "_id": bson.ObjectId("5a18152d1bb6270001c70352"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f6c51bb6270001bd0333"),
                "to_state": bson.ObjectId("5a17f7d21bb6270001bd034f"),
                "is_active": True,
                "label": "Approve",
                "event": "approve",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(1894890040029769162L)
            },
            {
                "_id": bson.ObjectId("5a1815701bb6270001c70373"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f7d21bb6270001bd034f"),
                "to_state": bson.ObjectId("5a17f78d1bb6270001bd0346"),
                "is_active": True,
                "label": "Seen",
                "event": "seen",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(2205967151884564606L)
            },
            {
                "_id": bson.ObjectId("5a18161e1bb6270001028cd0"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f78d1bb6270001bd0346"),
                "to_state": bson.ObjectId("5a17f7fc1bb6270001bd0359"),
                "is_active": True,
                "label": "Suspend",
                "event": "suspend",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(1854285483372474455L)
            },
            {
                "_id": bson.ObjectId("5a1816591bb6270001028cf6"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f7fc1bb6270001bd0359"),
                "to_state": bson.ObjectId("5a17f78d1bb6270001bd0346"),
                "is_active": True,
                "label": "Resume",
                "event": "resume",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(81389710212083104L)
            },
            {
                "_id": bson.ObjectId("5a1816c81bb6270001028d45"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f78d1bb6270001bd0346"),
                "to_state": bson.ObjectId("5a17f7391bb6270001bd033e"),
                "is_active": True,
                "label": "Expired",
                "event": "expired",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(2244054006097306867L)
            },
            {
                "_id": bson.ObjectId("5a1816dd1bb6270001028d5f"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f7391bb6270001bd033e"),
                "to_state": bson.ObjectId("5a17f78d1bb6270001bd0346"),
                "is_active": True,
                "label": "Seen",
                "event": "seen",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(2585664142032130717L)
            },
            {
                "_id": bson.ObjectId("5a1817071bb6270001028d7e"),
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "from_state": bson.ObjectId("5a17f7391bb6270001bd033e"),
                "to_state": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                "is_active": True,
                "label": "Expired",
                "event": "expired",
                "enable_manual": True,
                "on_enter_handlers": [],
                "on_leave_handlers": [],
                "bi_id": long(8194239664781898089L)
            }
        ])

    def backwards(self):
        pass
