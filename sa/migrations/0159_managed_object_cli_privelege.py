# ----------------------------------------------------------------------
# Managed Object CLI privilege settings
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
            "cli_privilege_policy",
            models.CharField(
                "CLI Privilege Policy",
                max_length=1,
                choices=[("E", "Raise privileges"), ("D", "Do not raise")],
                default="E",
            ),
        )
        # Profile settings
        self.db.add_column(
            "sa_managedobject",
            "cli_privilege_policy",
            models.CharField(
                "CLI Privilege Policy",
                max_length=1,
                choices=[("P", "From Profile"), ("E", "Raise privileges"), ("D", "Do not raise")],
                default="P",
            ),
        )
