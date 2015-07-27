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
from noc.lib.fields import DocumentReferenceField
from noc.lib.nosql import get_db


class Migration:
    depends_on = [
        ("main", "0055_default_pool")
    ]

    def forwards(self):
        db.add_column("sa_managedobject", "pool",
            DocumentReferenceField(
                "self", null=True, blank=True
            )
        )
        db.create_index(
            "sa_managedobject",
            ["pool"], unique=False, db_tablespace="")

    def backwards(self):
        db.delete_column("sa_managedobject", "pool")
