# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC models
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        # Get first segment
        ns = get_db().noc.networksegments.find_one({}, sort=[("name", 1)])
        db.execute(
            """
            UPDATE sa_managedobject
            SET segment=%s
            """,
            [str(ns["_id"])]
        )

    def backwards(self):
        pass
