# ----------------------------------------------------------------------
# peering point lg url
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
            "lg_rcmd",
            models.CharField("LG RCMD Url", max_length=128, blank=True, null=True),
        )
