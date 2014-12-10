# -*- coding: utf-8 -*-
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        db = get_db()
        scount = db.noc.pm.storages.count()
        if scount == 0:
            db.noc.pm.storages.insert({
                "name": "default",
                "collectors": [
                    {
                        "address": "127.0.0.1",
                        "port": 2003,
                        "protocol": "line",
                        "is_active": True,
                        "is_selectable": True
                    },
                    {
                        "address": "127.0.0.1",
                        "port": 2003,
                        "protocol": "udp",
                        "is_active": True,
                        "is_selectable": True
                    }
                ],
                "access": [
                    {
                        "protocol": "graphite",
                        "is_active": True,
                        "base_url": "http://127.0.0.1:8000/render"
                    }
                ],
                "description": "Default storage",
                "select_policy": "pri",
                "write_concern": 1
            })
        elif scount == 1:
            s = db.noc.pm.storages.find()[0]
            if "access" not in s or not s["access"]:
                db.noc.pm.storages.update({}, {
                    "$set": {
                        "collectors": [
                            {
                                "address": "127.0.0.1",
                                "port": 2003,
                                "protocol": "line",
                                "is_active": True,
                                "is_selectable": True
                            },
                            {
                                "address": "127.0.0.1",
                                "port": 2003,
                                "protocol": "udp",
                                "is_active": True,
                                "is_selectable": True
                            }
                        ],
                        "access": [
                            {
                                "protocol": "graphite",
                                "is_active": True,
                                "base_url": "http://127.0.0.1:8000/render"
                            }
                        ],
                        "select_policy": "pri",
                        "write_concern": 1
                    }
                })

    def backwards(self):
        pass