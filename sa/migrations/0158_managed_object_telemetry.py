# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object telemetry settings
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
            "box_discovery_telemetry_sample",
            models.IntegerField(
                "Box Discovery Telemetry Sample",
                default=0
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_telemetry_sample",
            models.IntegerField(
                "Periodic Discovery Telemetry Sample",
                default=0
            )
        )
        # Object settings
        db.add_column(
            "sa_managedobject",
            "box_discovery_telemetry_policy",
            models.CharField(
                "Box Discovery Telemetry Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable"),
                    ("P", "From Profile")
                ],
                default="P"
            )
        )
        db.add_column(
            "sa_managedobject",
            "box_discovery_telemetry_sample",
            models.IntegerField(
                "Box Discovery Telemetry Sample",
                default=0
            )
        )
        db.add_column(
            "sa_managedobject",
            "periodic_discovery_telemetry_policy",
            models.CharField(
                "Periodic Discovery Telemetry Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable"),
                    ("P", "From Profile")
                ],
                default="P"
            )
        )
        db.add_column(
            "sa_managedobject",
            "periodic_discovery_telemetry_sample",
            models.IntegerField(
                "Periodic Discovery Telemetry Sample",
                default=0
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "box_discovery_telemetry_sample")
        db.delete_column("sa_managedobjectprofile",
                         "periodic_discovery_telemetry_sample")
        db.delete_column("sa_managedobject",
                         "box_discovery_telemetry_policy")
        db.delete_column("sa_managedobject",
                         "box_discovery_telemetry_sample")
        db.delete_column("sa_managedobject",
                         "periodic_discovery_telemetry_policy")
        db.delete_column("sa_managedobject",
                         "periodic_discovery_telemetry_sample")
