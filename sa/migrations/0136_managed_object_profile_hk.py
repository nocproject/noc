# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile hk
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
        db.add_column("sa_managedobjectprofile", "enable_box_discovery_mac", models.BooleanField(default=False))

        db.add_column("sa_managedobjectprofile", "enable_box_discovery_hk", models.BooleanField(default=False))

        db.add_column(
            "sa_managedobjectprofile", "hk_handler",
            models.CharField("Housekeeping Handler", max_length=255, null=True, blank=True)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_mac")
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_hk")
        db.delete_column("sa_managedobjectprofile", "hk_handler")
