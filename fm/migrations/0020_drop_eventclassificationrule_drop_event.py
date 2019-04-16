# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# drop eventclassificationrule drop_event
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
        db.delete_column("fm_eventclassificationrule", "drop_event")

    def backwards(self):
        db.add_column("fm_eventclassificationrule", "drop_event", models.BooleanField("Drop Event", default=False))
        db.execute("UPDATE fm_eventclassificationrule SET drop_event=TRUE WHERE action='D'")
