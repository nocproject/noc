# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.lib.nosql import get_db
from noc.lib.dateutils import total_seconds


class Migration:
    def forwards(self):
        db = get_db()
        bulk = db.noc.fm.uptimes.initialize_unordered_bulk_op()
        n = 0
        for d in db.noc.fm.uptimes.find({}):
            bulk.find({"_id": d["_id"]}).update({
                "$set": {
                    "last_value": float(total_seconds(d["last"] - d["start"]))
                }
            })
            n += 1
        if n:
            bulk.execute()

    def backwards(self):
        pass
