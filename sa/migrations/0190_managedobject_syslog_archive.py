# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject.syslog_archive_policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        # ManagedObjectProfile
        db.add_column(
            "sa_managedobjectprofile",
            "syslog_archive_policy",
            models.CharField(
                "SYSLOG Archive Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="D"
            )
        )
        # ManagedObject
        db.add_column(
            "sa_managedobject",
            "syslog_archive_policy",
            models.CharField(
                "SYSLOG Archive Policy",
                max_length=1,
                choices=[
                    ("P", "Profile"),
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="P"
            )
        )

    def backwards(self):
        pass
