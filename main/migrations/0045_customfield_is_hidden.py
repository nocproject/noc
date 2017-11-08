# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Add .is_hidden field to CustomField
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("main_customfield", "is_hidden",
                      models.BooleanField("Is Hidden", default=False))

    def backwards(self):
        db.delete_column("main_customfield", "is_hidden")
