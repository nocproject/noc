# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db
## NOC models
from noc.core.model.fields import DocumentReferenceField
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        mdb = get_db()
        for d in mdb.noc.pools.find():
            pid = int(d["name"][1:])
            db.execute(
                "UPDATE sa_managedobject SET pool=%s WHERE activator_id=%s",
                [str(d["_id"]), pid]
            )

    def backwards(self):
        pass