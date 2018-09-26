# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC models
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        mdb = get_db()
        for d in mdb.noc.pools.find():
            pid = int(d["name"][1:])
            db.execute(
                "UPDATE sa_managedobject SET pool=%s WHERE activator_id=%s",
                [str(d["_id"]), pid]
            )
        # Adjust scheme values
        # For smooth develop -> post-microservice migration
        db.execute("UPDATE sa_managedobject SET scheme = scheme + 1")

    def backwards(self):
        pass
