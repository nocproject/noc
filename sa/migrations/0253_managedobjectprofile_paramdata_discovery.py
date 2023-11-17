# ----------------------------------------------------------------------
# ManagedObjectProfile enable box discovery_param_data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
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
            "enable_box_discovery_param_data",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_param_data_conflict_resolve_policy",
            models.CharField(
                "CPE discovery mode (full or status only)",
                max_length=1,
                choices=[("M", "Manual"), ("D", "Prefer Discovery"), ("O", "Prefer Object")],
                default="O",
            ),
        )
