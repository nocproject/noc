# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# rule drop event
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
        db.add_column("fm_eventclassificationrule", "drop_event", models.BooleanField("Drop Event", default=False))

    def backwards(self):
        db.delete_column("fm_eventclassificationrule", "drop_event")
