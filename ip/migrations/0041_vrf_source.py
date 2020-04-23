# ----------------------------------------------------------------------
# VRF.source
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
            "ip_vrf",
            "source",
            models.CharField(
                "Source",
                max_length=1,
                choices=[("M", "Manual"), ("i", "Interface"), ("m", "MPLS")],
                null=False,
                blank=False,
                default="M",
            ),
        )
