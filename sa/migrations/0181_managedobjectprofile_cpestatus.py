# ----------------------------------------------------------------------
# ManagedObjectProfile enable box, periodic discovery_cpestatus
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
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_cpestatus",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_cpestatus_policy",
            models.CharField(
                "CPE discovery mode (full or status only)",
                max_length=1,
                choices=[("S", "Status Only"), ("F", "Full")],
                default="S",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_periodic_discovery_cpestatus",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_cpestatus_policy",
            models.CharField(
                "CPE discovery mode (full or status only)",
                max_length=1,
                choices=[("S", "Status Only"), ("F", "Full")],
                default="S",
            ),
        )
