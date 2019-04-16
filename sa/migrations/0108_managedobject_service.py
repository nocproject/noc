# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
# NOC models
from noc.core.model.fields import DocumentReferenceField


class Migration(object):
    depends_on = [("main", "0055_default_pool")]

    def forwards(self):
        db.add_column("sa_managedobject", "service", DocumentReferenceField("self", null=True, blank=True))
        db.create_index("sa_managedobject", ["service"], unique=False, db_tablespace="")

    def backwards(self):
        db.delete_column("sa_managedobject", "service")
