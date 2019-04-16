# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# eventtrigger handler
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
        db.add_column("fm_eventtrigger", "handler", models.CharField("Handler", max_length=128, null=True, blank=True))

    def backwards(self):
        db.drop_column("fm_eventtrigger", "handler")
