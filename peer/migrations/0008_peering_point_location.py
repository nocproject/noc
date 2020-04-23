# ----------------------------------------------------------------------
# peering point location
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
            "peer_peeringpoint",
            "location",
            models.CharField("Location", max_length=64, blank=True, null=True),
        )
