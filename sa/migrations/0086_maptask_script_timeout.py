# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# maptask script_timeout
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
        db.add_column("sa_maptask", "script_timeout", models.IntegerField("Script timeout", null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_maptask", "script_timeout")
