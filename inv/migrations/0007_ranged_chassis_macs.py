# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Migrate chassis ids to ranged version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Migrate chassis ids to ranged version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        c = db.noc.inv.discovery_id
        for r in c.find({
            "first_chassis_mac": {"$exists": True},
            "last_chassis_mac": {"$exists": True}
        }):
            c.update(
                {"_id": r["_id"]},
                {
                    "$unset": {
                        "first_chassis_mac": "",
                        "last_chassis_mac": ""
                    },
                    "$set": {
                        "chassis_mac": [
                            {
                                "first_mac": r["first_chassis_mac"],
                                "last_mac": r["last_chassis_mac"]
                            }
                        ]
                    }
                }
            )

    def backwards(self):
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
