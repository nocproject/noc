# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# notification link
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
        db.add_column("main_notification", "link", models.CharField("Link", max_length=256, null=True, blank=True))

    def backwards(self):
        db.delete_column("main_notification", "link")
