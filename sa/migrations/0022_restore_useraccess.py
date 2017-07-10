# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.execute("DELETE FROM sa_useraccess")
        for id, name in db.execute(
            "SELECT id,name FROM sa_managedobjectselector WHERE name LIKE 'NOC_UA_%%'"):
            uid, n = name[7:].split("_")
            db.execute(
                "INSERT INTO sa_useraccess(user_id,selector_id) VALUES(%s,%s)"
                , [int(uid), id])


    def backwards(self):
        "Write your backwards migration here"
