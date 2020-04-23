# ----------------------------------------------------------------------
# ManagedObjectProfile config fetch settings
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
            "config_fetch_policy",
            models.CharField(
                "Config Fetch Policy",
                max_length=1,
                choices=[("s", "Startup"), ("r", "Running")],
                default="r",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "config_fetch_policy",
            models.CharField(
                "Config Fetch Policy",
                max_length=1,
                choices=[("P", "From Profile"), ("s", "Startup"), ("r", "Running")],
                default="P",
            ),
        )
