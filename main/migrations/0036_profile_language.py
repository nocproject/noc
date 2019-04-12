# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# profile language
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
        db.delete_column("main_userprofile", "preferred_language_id")
        db.add_column(
            "main_userprofile", "preferred_language",
            models.CharField("Preferred Language", max_length=16, null=True, blank=True)
        )

    def backwards(self):
        pass
