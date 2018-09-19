# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Set workflow fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    depends_on = [
        ("wf", "0001_default_wf")
    ]

    def forwards(self):
        s_map = {
            "N": bson.ObjectId("5a17f61b1bb6270001bd0328"),
            "F": bson.ObjectId("5a17f61b1bb6270001bd0328"),
            "A": bson.ObjectId("5a17f78d1bb6270001bd0346"),
            "R": bson.ObjectId("5a17f6c51bb6270001bd0333"),
            "O": bson.ObjectId("5a17f7fc1bb6270001bd0359"),
            "C": bson.ObjectId("5a17f7391bb6270001bd033e")
        }
        db = get_db()
        db["noc.phonerangeprofiles"].update_many(
            {}, {
                "$set": {
                    "workflow": bson.ObjectId("5a1d078e1bb627000151a17d")  # Default
                }
            })
        db["noc.phoneranges"].update_many(
            {}, {
                "$set": {
                    "state": bson.ObjectId("5a1d07b41bb627000151a18b")  # Ready
                }
            }
        )
        db["noc.phonenumberprofiles"].update_many(
            {}, {
                "$set": {
                    "workflow": bson.ObjectId("5a01d980b6f529000100d37a")  # Default Resource
                }
            })
        for s in s_map:
            db["noc.phonenumbers"].update_many({
                "status": s
            }, {
                "$set": {
                    "state": s_map[s]
                }
            })

    def backwards(self):
        pass
