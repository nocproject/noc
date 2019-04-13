# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject tt_queue
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
        db.add_column("sa_managedobject", "tt_queue", models.CharField(max_length=64, null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "tt_queue")
