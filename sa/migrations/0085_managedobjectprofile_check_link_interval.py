# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile check_link interval
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
        # Alter sa_managedobjectprofile
        db.add_column(
            "sa_managedobjectprofile", "check_link_interval",
            models.CharField("check_link interval", max_length=256, blank=True, null=True, default=",60")
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "check_link_interval")
