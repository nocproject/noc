# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile ping interval
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
        db.add_column("sa_managedobjectprofile", "ping_interval", models.IntegerField("Ping interval", default=60))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "ping_interval")
