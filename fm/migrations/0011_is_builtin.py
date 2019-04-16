# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Add EventClass.is_builtin and EventClassificationRule.is_builtin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        db.add_column("fm_eventclass", "is_builtin", models.BooleanField("Is Builtin", default=False))
        db.add_column("fm_eventclassificationrule", "is_builtin", models.BooleanField("Is Builtin", default=False))

    def backwards(self):
        db.delete_column("fm_eventclass", "is_builtin")
        db.delete_column("fm_eventclassificationrule", "is_builtin")
