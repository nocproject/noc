# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Migration:
    def forwards(self):
        from noc.lib.nosql import get_db
<<<<<<< HEAD
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
=======

        f = """db.%(collection)s.find({repeats: {$exists: false}}).forEach(
            function(e) {
                e.repeats = 1;
                e.start_timestamp = e.timestamp;
                db.%(collection)s.save(e);
            })
        """
        db = get_db()
        db.eval(f % {"collection": "noc.events.active"})
        db.eval(f % {"collection": "noc.events.archive"})
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def backwards(self):
        pass
