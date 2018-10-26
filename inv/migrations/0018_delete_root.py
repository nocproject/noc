# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Delete Root nodes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        # Get root model id
        rm = db["noc.objectmodels"].find_one({
            "name": "Root"
        })
        if not rm:
            return  # No root model
        # Get root container
        c = db["noc.objects"]
        rc = c.find_one({
            "model": rm["_id"]
        })
        if not rc:
            return
        # Remove root references
        c.update_many({
            "container": rc["_id"]
        }, {
            "$set": {
                "container": None
            }
        })
        # Remove root container
        c.delete_one({
            "_id": rc["_id"]
        })

    def backwards(self):
        pass
