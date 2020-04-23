# ----------------------------------------------------------------------
# Managed Object telemetry settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Profile settings
        self.db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_telemetry_sample",
            models.IntegerField("Box Discovery Telemetry Sample", default=0),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_telemetry_sample",
            models.IntegerField("Periodic Discovery Telemetry Sample", default=0),
        )
        # Object settings
        self.db.add_column(
            "sa_managedobject",
            "box_discovery_telemetry_policy",
            models.CharField(
                "Box Discovery Telemetry Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
                default="P",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "box_discovery_telemetry_sample",
            models.IntegerField("Box Discovery Telemetry Sample", default=0),
        )
        self.db.add_column(
            "sa_managedobject",
            "periodic_discovery_telemetry_policy",
            models.CharField(
                "Periodic Discovery Telemetry Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
                default="P",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "periodic_discovery_telemetry_sample",
            models.IntegerField("Periodic Discovery Telemetry Sample", default=0),
        )
