# ----------------------------------------------------------------------
# ManagedObjectProfile discovery running policy
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
            "box_discovery_running_policy",
            models.CharField(
                "Box Running Policy",
                choices=[("R", "Require Up"), ("r", "Require if enabled"), ("i", "Ignore")],
                max_length=1,
                default="R",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_running_policy",
            models.CharField(
                "Periodic Running Policy",
                choices=[("R", "Require Up"), ("r", "Require if enabled"), ("i", "Ignore")],
                max_length=1,
                default="R",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "box_discovery_running_policy",
            models.CharField(
                "Box Running Policy",
                choices=[
                    ("P", "From Profile"),
                    ("R", "Require Up"),
                    ("r", "Require if enabled"),
                    ("i", "Ignore"),
                ],
                max_length=1,
                default="P",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "periodic_discovery_running_policy",
            models.CharField(
                "Periodic Running Policy",
                choices=[
                    ("P", "From Profile"),
                    ("R", "Require Up"),
                    ("r", "Require if enabled"),
                    ("i", "Ignore"),
                ],
                max_length=1,
                default="P",
            ),
        )
