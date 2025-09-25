# ----------------------------------------------------------------------
# ManagedObjectProfile confdb raw policy
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
            "confdb_raw_policy",
            models.CharField(
                "ConfDB Raw Policy",
                max_length=1,
                choices=[("D", "Disable"), ("E", "Enable")],
                default="D",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "confdb_raw_policy",
            models.CharField(
                "ConfDB Raw Policy",
                max_length=1,
                choices=[("P", "Profile"), ("D", "Disable"), ("E", "Enable")],
                default="P",
            ),
        )
