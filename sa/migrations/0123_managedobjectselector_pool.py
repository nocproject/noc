# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectselector pool
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
        db.add_column("sa_managedobjectselector", "filter_pool", DocumentReferenceField("self", null=True, blank=True))
        db.create_index("sa_managedobjectselector", ["filter_pool"], unique=False, db_tablespace="")

    def backwards(self):
        db.delete_column("sa_managedobjectselector", "filter_pool")
