# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("fm_eventclassificationrule", "drop_event", models.BooleanField("Drop Event", default=False))

    def backwards(self):
        db.delete_column("fm_eventclassificationrule", "drop_event")
