# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class Migration:
    def forwards(self):
        from noc.lib.nosql import get_db
        db = get_db()
        for c in [db.noc.events.active, db.noc.events.archive]:
            # @todo: Set start_timestamp = timestamp
            c.update(
                {"repeats": {"$exists": False}},
                {
                    "$set": {
                        "repeats": 1
                    }
                }
            )

    def backwards(self):
        pass
