# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("cm_objectcategory", "notify_immediately",
                      models.TextField("Notify Immediately", blank=True, null=True))
        db.add_column("cm_objectcategory", "notify_delayed", models.TextField("Notify Delayed", blank=True, null=True))

    def backwards(self):
        db.delete_column("cm_objectcategory", "notify_immediately")
        db.delete_column("cm_objectcategory", "notify_delayed")
