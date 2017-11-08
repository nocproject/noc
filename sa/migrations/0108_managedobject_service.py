# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC models
from noc.core.model.fields import DocumentReferenceField
# Django modules
# Third-party modules
from south.db import db


class Migration:
    depends_on = [
        ("main", "0055_default_pool")
    ]

    def forwards(self):
        db.add_column("sa_managedobject", "service",
                      DocumentReferenceField(
                          "self", null=True, blank=True
                      )
                      )
        db.create_index(
            "sa_managedobject",
            ["service"], unique=False, db_tablespace="")

    def backwards(self):
        db.delete_column("sa_managedobject", "service")
