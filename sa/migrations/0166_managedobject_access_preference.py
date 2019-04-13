# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object Access Preference
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
        # Profile settings
        db.add_column(
            "sa_managedobjectprofile", "access_preference",
            models.CharField(
                "Access Preference",
                max_length=8,
                choices=[("S", "SNMP Only"), ("C", "CLI Only"), ("SC", "SNMP, CLI"), ("CS", "CLI, SNMP")],
                default="CS"
            )
        )
        # Profile settings
        db.add_column(
            "sa_managedobject", "access_preference",
            models.CharField(
                "Access Preference",
                max_length=8,
                choices=[
                    ("P", "Profile"), ("S", "SNMP Only"), ("C", "CLI Only"), ("SC", "SNMP, CLI"), ("CS", "CLI, SNMP")
                ],
                default="P"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "access_preference")
        db.delete_column("sa_managedobject", "access_preference")
