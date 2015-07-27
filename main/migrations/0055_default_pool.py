# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Create *default* pool
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC modules
from noc.lib.nosql import get_db

class Migration:
    depends_on = [
        ("sa", "0005_activator")
    ]

    def forwards(self):
        mdb = get_db()
        for a_id, name in db.execute("SELECT id, name FROM sa_activator"):
            mdb.noc.pools.insert({
                "name": "P%04d" % a_id,
                "description": name
            })

    def backwards(self):
        pass
