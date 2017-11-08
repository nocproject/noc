# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Create sa_managedobjectprofjle.enable_periodic_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_metrics",
            models.BooleanField(default=False)
        )

    def backwards(self):
        pass
