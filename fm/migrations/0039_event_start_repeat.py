# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class Migration:
    def forwards(self):
        from noc.lib.nosql import get_db

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

    def backwards(self):
        pass
