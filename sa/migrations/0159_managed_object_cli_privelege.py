# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object CLI privilege settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        # Profile settings
        db.add_column(
            "sa_managedobjectprofile",
            "cli_privilege_policy",
            models.CharField(
                "CLI Privilege Policy",
                max_length=1,
                choices=[
                    ("E", "Raise privileges"),
                    ("D", "Do not raise")
                ],
                default="E"
            )
        )
        # Profile settings
        db.add_column(
            "sa_managedobject",
            "cli_privilege_policy",
            models.CharField(
                "CLI Privilege Policy",
                max_length=1,
                choices=[
                    ("P", "From Profile"),
                    ("E", "Raise privileges"),
                    ("D", "Do not raise")
                ],
                default="P"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "cli_privilege_policy")
        db.delete_column("sa_managedobject",
                         "cli_privilege_policy")
