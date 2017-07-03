# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Move InterfaceProfile.mac_discovery to .mac_discovery_policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        coll = db["noc.interface_profiles"]
        for d in list(coll.find({}, {"_id": 1, "mac_discovery": 1})):
            coll.update({
                "_id": d["_id"]
            }, {
                "$set": {
                    "mac_discovery_policy": "e" if d.get("mac_discovery") else "d"
                },
                "$unset": {
                    "mac_discovery": 1
                }
            })

    def backwards(self):
        pass
