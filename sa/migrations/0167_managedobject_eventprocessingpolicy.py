# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject.event_processing_policy
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
            "event_processing_policy",
            models.CharField(
                "Event Processing Policy",
                max_length=1,
                choices=[
                    ("E", "Process Events"),
                    ("D", "Drop events")
                ],
                default="E"
            )
        )
        # Object settings
        db.add_column(
            "sa_managedobject",
            "event_processing_policy",
            models.CharField(
                "Event Processing Policy",
                max_length=1,
                choices=[
                    ("P", "Profile"),
                    ("E", "Process Events"),
                    ("D", "Drop events")
                ],
                default="P"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "event_processing_policy")
        db.delete_column("sa_managedobject",
                         "event_processing_policy")
