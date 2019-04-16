# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject container
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
    def forwards(self):
        db.add_column("sa_managedobject", "container", DocumentReferenceField("self", null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "container")
