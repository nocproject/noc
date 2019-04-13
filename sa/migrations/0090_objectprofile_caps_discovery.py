# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile caps discovery
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
            "sa_managedobjectprofile", "enable_caps_discovery",
            models.BooleanField("Enable caps discovery", default=True)
        )
        db.add_column(
            "sa_managedobjectprofile", "caps_discovery_min_interval",
            models.IntegerField("Min. caps discovery interval", default=600)
        )
        db.add_column(
            "sa_managedobjectprofile", "caps_discovery_max_interval",
            models.IntegerField("Max. caps discovery interval", default=86400)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_caps_discovery")
        db.delete_column("sa_managedobjectprofile", "caps_discovery_min_interval")
        db.delete_column("sa_managedobjectprofile", "caps_discovery_max_interval")
