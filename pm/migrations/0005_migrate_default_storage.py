# ----------------------------------------------------------------------
# migrate default storage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        scount = db.noc.pm.storages.count_documents({})
        if scount == 0:
            db.noc.pm.storages.insert_one(
                {
                    "name": "default",
                    "collectors": [
                        {
                            "address": "127.0.0.1",
                            "port": 2003,
                            "protocol": "line",
                            "is_active": True,
                            "is_selectable": True,
                        },
                        {
                            "address": "127.0.0.1",
                            "port": 2003,
                            "protocol": "udp",
                            "is_active": True,
                            "is_selectable": True,
                        },
                    ],
                    "access": [
                        {
                            "protocol": "graphite",
                            "is_active": True,
                            "base_url": "http://127.0.0.1:8000/render",
                        }
                    ],
                    "description": "Default storage",
                    "select_policy": "pri",
                    "write_concern": 1,
                }
            )
        elif scount == 1:
            s = db.noc.pm.storages.find()[0]
            if "access" not in s or not s["access"]:
                db.noc.pm.storages.update_many(
                    {},
                    {
                        "$set": {
                            "collectors": [
                                {
                                    "address": "127.0.0.1",
                                    "port": 2003,
                                    "protocol": "line",
                                    "is_active": True,
                                    "is_selectable": True,
                                },
                                {
                                    "address": "127.0.0.1",
                                    "port": 2003,
                                    "protocol": "udp",
                                    "is_active": True,
                                    "is_selectable": True,
                                },
                            ],
                            "access": [
                                {
                                    "protocol": "graphite",
                                    "is_active": True,
                                    "base_url": "http://127.0.0.1:8000/render",
                                }
                            ],
                            "select_policy": "pri",
                            "write_concern": 1,
                        }
                    },
                )
