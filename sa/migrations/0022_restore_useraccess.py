# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# restore useraccess
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute("DELETE FROM sa_useraccess")
        for id, name in db.execute("SELECT id,name FROM sa_managedobjectselector WHERE name LIKE 'NOC_UA_%%'"):
            uid, n = name[7:].split("_")
            db.execute("INSERT INTO sa_useraccess(user_id,selector_id) VALUES(%s,%s)", [int(uid), id])

    def backwards(self):
        pass
