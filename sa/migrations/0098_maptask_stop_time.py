# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# maptask stop_time
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
        db.execute("DELETE FROM sa_maptask")
        db.execute("DELETE FROM sa_reducetask")
        db.add_column("sa_maptask", "stop_time", models.DateTimeField())

    def backwards(self):
        db.delete_column("sa_maptask", "stop_time")
