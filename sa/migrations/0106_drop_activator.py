# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
## Third-party modules
from south.db import db
## NOC models


class Migration:
    depends_on = [
        ("main", "0033_shard")
    ]

    def forwards(self):
        db.delete_column(
            "sa_managedobjectselector",
            "filter_activator_id"
        )
        db.drop_table("sa_activator")
        db.drop_table("sa_collector")
        db.drop_table("main_shard")

    def backwards(self):
        pass
