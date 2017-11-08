# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object Access Preference
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        # Profile settings
        db.add_column(
            "sa_managedobjectprofile",
            "access_preference",
            models.CharField(
                "Access Preference",
                max_length=8,
                choices=[
                    ("S", "SNMP Only"),
                    ("C", "CLI Only"),
                    ("SC", "SNMP, CLI"),
                    ("CS", "CLI, SNMP")
                ],
                default="CS"
            )
        )
        # Profile settings
        db.add_column(
            "sa_managedobject",
            "access_preference",
            models.CharField(
                "Access Preference",
                max_length=8,
                choices=[
                    ("P", "Profile"),
                    ("S", "SNMP Only"),
                    ("C", "CLI Only"),
                    ("SC", "SNMP, CLI"),
                    ("CS", "CLI, SNMP")
                ],
                default="P"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "access_preference")
        db.delete_column("sa_managedobject",
                         "access_preference")
