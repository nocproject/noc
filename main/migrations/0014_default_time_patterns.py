# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# default time pattern
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db

TIME_PATTERNS = [("Any", "Always match", []), ("Workdays", "Match workdays", ["mon-fri"])]


class Migration(object):
    def forwards(self):
        for name, desc, tpd in TIME_PATTERNS:
            if db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s", [name])[0][0] == 0:
                db.execute("INSERT INTO main_timepattern(name,description) VALUES(%s,%s)", [name, desc])
                tp_id = db.execute("SELECT id FROM main_timepattern WHERE name=%s", [name])[0][0]
                for tp in tpd:
                    db.execute("INSERT INTO main_timepatternterm(time_pattern_id,term) VALUES(%s,%s)", [tp_id, tp])

    def backwards(self):
        pass
