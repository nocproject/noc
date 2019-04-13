# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject segment
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
    depends_on = [("inv", "0010_default_segment")]

    def forwards(self):
        db.add_column("sa_managedobject", "segment", DocumentReferenceField("self", null=True, blank=True))
        db.create_index("sa_managedobject", ["segment"], unique=False, db_tablespace="")

    def backwards(self):
        db.delete_column("sa_managedobject", "segment")
