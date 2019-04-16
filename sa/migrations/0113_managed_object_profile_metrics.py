# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile metrics
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
            "sa_managedobjectprofile", "enable_periodic_discovery_metrics", models.BooleanField(default=False)
        )

    def backwards(self):
        pass
