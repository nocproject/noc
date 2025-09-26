# ----------------------------------------------------------------------
# ManagedObjectProfile dynamic classification policy
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
            "dynamic_classification_policy",
            models.CharField(
                "Dynamic Classification Policy",
                max_length=1,
                choices=[("D", "Disable"), ("R", "By Rule")],
                default="R",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "dynamic_classification_policy",
            models.CharField(
                "Dynamic Classification Policy",
                max_length=1,
                choices=[("P", "Profile"), ("D", "Disable"), ("R", "By Rule")],
                default="P",
            ),
        )
