# ----------------------------------------------------------------------
# Add Resource Group to vc domainprovisioning
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
            "vc_vcdomainprovisioningconfig",
            "resource_group",
            models.CharField("Resource Group", max_length=64, null=True, blank=True),
        )
