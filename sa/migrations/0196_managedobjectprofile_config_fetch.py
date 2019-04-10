# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectProfile config fetch settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models
# NOC modules


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "config_fetch_policy",
            models.CharField(
                "Config Fetch Policy",
                max_length=1,
                choices=[
                    ("s", "Startup"),
                    ("r", "Running")
                ],
                default="r"
            )
        )
        db.add_column(
            "sa_managedobject",
            "config_fetch_policy",
            models.CharField(
                "Config Fetch Policy",
                max_length=1,
                choices=[
                    ("P", "From Profile"),
                    ("s", "Startup"),
                    ("r", "Running")
                ],
                default="P"
            )
        )

    def backwards(self):
        pass
