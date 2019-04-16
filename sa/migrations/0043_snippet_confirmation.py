# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# snippet confirmation
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
    depends_on = [
        ("main", "0035_prefix_table"),
    ]

    def forwards(self):
        db.add_column(
            "sa_commandsnippet", "require_confirmation", models.BooleanField("Require Confirmation", default=False)
        )

    def backwards(self):
        db.delete_column("sa_commandsnippet", "require_confirmation")
