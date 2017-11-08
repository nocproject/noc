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
    def forwards(self):
        db.add_column("sa_managedobject", "container",
                      DocumentReferenceField(
                          "self", null=True, blank=True
                      )
                      )

    def backwards(self):
        db.delete_column("sa_managedobject", "container")
