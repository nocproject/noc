# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile ndp
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
        db.add_column("sa_managedobjectprofile", "enable_box_discovery_huawei_ndp", models.BooleanField(default=False))
        db.add_column(
            "sa_managedobjectprofile", "enable_box_discovery_mikrotik_ndp", models.BooleanField(default=False)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_huawei_ndp")
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_mikrotik_ndp")
