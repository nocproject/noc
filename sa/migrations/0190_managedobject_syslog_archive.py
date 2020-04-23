# ----------------------------------------------------------------------
# ManagedObject.syslog_archive_policy
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
        # ManagedObjectProfile
        self.db.add_column(
            "sa_managedobjectprofile",
            "syslog_archive_policy",
            models.CharField(
                "SYSLOG Archive Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable")],
                default="D",
            ),
        )
        # ManagedObject
        self.db.add_column(
            "sa_managedobject",
            "syslog_archive_policy",
            models.CharField(
                "SYSLOG Archive Policy",
                max_length=1,
                choices=[("P", "Profile"), ("E", "Enable"), ("D", "Disable")],
                default="P",
            ),
        )
