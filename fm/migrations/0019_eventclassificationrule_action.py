# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# eventclassificationrule action
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
        db.add_column(
            "fm_eventclassificationrule", "action",
            models.CharField(
                "Action", max_length=1, choices=[("A", "Make Active"), ("C", "Close"), ("D", "Drop")], default="A"
            )
        )
        db.execute("UPDATE fm_eventclassificationrule SET action='D' WHERE drop_event=TRUE")

    def backwards(self):
        db.delete_column("fm_eventclassificationrule", "action")
