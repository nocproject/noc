# ----------------------------------------------------------------------
# managedobjectprofile cli_session_policy
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
            "cli_session_policy",
            models.CharField(
                "CLI Session Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable")],
                default="E",
            ),
        )
        # Object settings
        self.db.add_column(
            "sa_managedobject",
            "cli_session_policy",
            models.CharField(
                "CLI Session Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
                default="P",
            ),
        )
