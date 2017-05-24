# -*- coding: utf-8 -*-
# #----------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        db.add_column(
            "main_userprofile", "preview_theme",
            models.CharField("Preview Theme",
                             max_length=32, null=True, blank=True))

    def backwards(self):
        db.drop_column("main_userprofile", "preview_theme_id")
