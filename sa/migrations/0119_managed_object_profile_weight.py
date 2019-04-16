# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile weight
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
        db.add_column("sa_managedobjectprofile", "weight", models.IntegerField("Alarm weight", default=0))
        db.delete_column("sa_managedobjectprofile", "check_link_interval")
        db.delete_column("sa_managedobjectprofile", "down_severity")

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "report_ping_rtt")
