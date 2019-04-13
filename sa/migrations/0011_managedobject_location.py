# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject location
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from django.db import models
from south.db import db


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobject", "location", models.CharField("Location", max_length=256, null=True, blank=True)
        )

    def backwards(self):
        db.delete_column("sa_managedobject", "location")
