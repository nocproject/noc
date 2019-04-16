# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# snippet permissions
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
        db.add_column(
            "sa_commandsnippet", "permission_name",
            models.CharField("Permission Name", max_length=64, null=True, blank=True)
        )
        db.add_column("sa_commandsnippet", "display_in_menu", models.BooleanField("Show in menu", default=False))

    def backwards(self):
        db.delete_column("sa_commandsnippet", "permission_name")
        db.delete_column("sa_commandsnippet", "display_in_menu")
