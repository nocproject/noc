# ----------------------------------------------------------------------
# Add Resource Group to ObjectNotification and ResourceGroup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_objectnotification",
            "resource_group",
            models.CharField("Resource Group", max_length=64, null=True, blank=True),
        )
        self.db.add_column(
            "sa_commandsnippet",
            "resource_group",
            models.CharField("Resource Group", max_length=64, null=True, blank=True),
        )
