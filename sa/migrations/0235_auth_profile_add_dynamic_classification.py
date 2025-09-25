# ----------------------------------------------------------------------
# Auth Profile dynamic classification policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_authprofile",
            "dynamic_classification_policy",
            models.CharField(
                "Dynamic Classification Policy",
                max_length=1,
                choices=[("D", "Disable"), ("R", "By Rule"), ("U", "By Username/SNMP RO")],
                default="R",
            ),
        )
        self.db.add_column(
            "sa_authprofile",
            "match_rules",
            models.JSONField("Match Dynamic Rules", null=True, blank=True, default=lambda: "[]"),
        )
