# ----------------------------------------------------------------------
# Managed Object Access Preference
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
            "access_preference",
            models.CharField(
                "Access Preference",
                max_length=8,
                choices=[
                    ("S", "SNMP Only"),
                    ("C", "CLI Only"),
                    ("SC", "SNMP, CLI"),
                    ("CS", "CLI, SNMP"),
                ],
                default="CS",
            ),
        )
        # Profile settings
        self.db.add_column(
            "sa_managedobject",
            "access_preference",
            models.CharField(
                "Access Preference",
                max_length=8,
                choices=[
                    ("P", "Profile"),
                    ("S", "SNMP Only"),
                    ("C", "CLI Only"),
                    ("SC", "SNMP, CLI"),
                    ("CS", "CLI, SNMP"),
                ],
                default="P",
            ),
        )
