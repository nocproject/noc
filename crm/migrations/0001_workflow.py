# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Set workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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
        db = get_db()
        wf = bson.ObjectId("5a1d078e1bb627000151a17d")
        state = bson.ObjectId("5a1d07b41bb627000151a18b")
        db["noc.supplierprofiles"].update_many({}, {
            "$set": {
                "workflow": wf
            }
        })
        db["noc.subscriberprofiles"].update_many({}, {
            "$set": {
                "workflow": wf
            }
        })
        db["noc.subscribers"].update_many({}, {
            "$set": {
                "state": state
            }
        })
        db["noc.suppliers"].update_many({}, {
            "$set": {
                "state": state
            }
        })

    def backwards(self):
        pass
