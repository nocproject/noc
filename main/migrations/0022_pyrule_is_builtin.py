# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# pyrule is_builtin
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
        db.add_column("main_pyrule", "is_builtin", models.BooleanField("Is Builtin", default=False))

    def backwards(self):
        db.delete_column("main_pyrule", "is_builtin")
