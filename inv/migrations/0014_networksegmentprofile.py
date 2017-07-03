# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Create default NetworkSegmentProfile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import bson
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        coll = db["noc.networksegmentprofiles"]
        result = coll.insert({
            "name": "default",
            "description": "Default segment profile",
            "mac_discovery_interval": 86400,
            "mac_restrict_to_management_vlan": False,
            "enable_lost_redundancy": True,
            "topology_methods": [
                {
                    "method": m,
                    "is_active": True
                } for m in ["oam", "lacp", "udld", "lldp", "cdp",
                            "huawei_ndp", "stp", "nri"]
            ]
        })
        if isinstance(result, bson.ObjectId):
            profile_id = result
        else:
            profile_id = result.inserted_id

        db["noc.networksegments"].update({}, {
            "$set": {
                "profile": profile_id
            }
        }, multi=True)

    def backwards(self):
        pass
