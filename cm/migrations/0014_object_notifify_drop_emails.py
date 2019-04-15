# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# object notify drop emails
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.drop_column("cm_objectnotify", "emails")
        db.execute("ALTER TABLE cm_objectnotify ALTER COLUMN notification_group_id SET NOT NULL")

    def backwards(self):
        db.add_column("cm_objectnotify", "emails", models.CharField("Emails", max_length=128))
