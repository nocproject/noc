# ----------------------------------------------------------------------
# *.*_discovery_policy
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
        self.db.delete_column("ip_prefix", "enable_ip_discovery")
        self.db.add_column(
            "ip_prefix",
            "prefix_discovery_policy",
            models.CharField(
                "Prefix Discovery Policy",
                max_length=1,
                choices=[("P", "Profile"), ("E", "Enable"), ("D", "Disable")],
                default="P",
                blank=False,
                null=False,
            ),
        )
        self.db.add_column(
            "ip_prefix",
            "address_discovery_policy",
            models.CharField(
                "Address Discovery Policy",
                max_length=1,
                choices=[("P", "Profile"), ("E", "Enable"), ("D", "Disable")],
                default="P",
                blank=False,
                null=False,
            ),
        )
