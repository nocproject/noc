# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectProfile.denied_firmware_policy
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
        # ManagedObjectProfile
        db.add_column(
            "sa_managedobjectprofile", "new_platform_creation_policy",
            models.CharField(
                "New Platform Creation Policy", max_length=1, choices=[("C", "Create"), ("A", "Alarm")], default="C"
            )
        )
        db.add_column(
            "sa_managedobjectprofile", "denied_firmware_policy",
            models.CharField(
                "Firmware Policy",
                max_length=1,
                choices=[("I", "Ignore"), ("s", "Ignore&Stop"), ("A", "Raise Alarm"), ("S", "Raise Alarm&Stop")],
                default="I"
            )
        )
        # ManagedObject
        db.add_column(
            "sa_managedobject", "denied_firmware_policy",
            models.CharField(
                "Firmware Policy",
                max_length=1,
                choices=[
                    ("P", "Profile"), ("I", "Ignore"), ("s", "Ignore&Stop"), ("A", "Raise Alarm"),
                    ("S", "Raise Alarm&Stop")
                ],
                default="P"
            )
        )

    def backwards(self):
        pass
