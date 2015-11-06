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


class Migration:
    depends_on = [
        ("inv", "0010_default_segment")
    ]

    def forwards(self):
        db.add_column("sa_managedobject", "segment",
            DocumentReferenceField(
                "self", null=True, blank=True)
        )
        db.create_index(
            "sa_managedobject",
            ["segment"], unique=False, db_tablespace="")

    def backwards(self):
        db.delete_column("sa_managedobject", "segment")
