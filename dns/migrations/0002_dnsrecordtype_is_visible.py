# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# zonerecordtype is visible
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
        db.add_column("dns_dnszonerecordtype", "is_visible", models.BooleanField("Is Visible?", default=True))

    def backwards(self):
        db.delete_column("dns_dnszonerecordtype", "is_visible")
