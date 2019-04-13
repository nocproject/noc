# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# activator caps
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
        db.add_column("sa_activator", "min_sessions", models.IntegerField("Min Sessions", default=0))
        db.add_column("sa_activator", "min_members", models.IntegerField("Min Members", default=0))

    def backwards(self):
        db.delete_column("sa_activator", "min_sessions")
        db.delete_column("sa_activator", "min_members")
