# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# event start repeat
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        for c in [db.noc.events.active, db.noc.events.archive]:
            # @todo: Set start_timestamp = timestamp
            c.update_many({"repeats": {"$exists": False}}, {"$set": {"repeats": 1}})

    def backwards(self):
        pass
