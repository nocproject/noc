# ----------------------------------------------------------------------
# peer status
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
            "peer_peer",
            "status",
            models.CharField(
                "Status",
                max_length=1,
                default="A",
                choices=[("P", "Planned"), ("A", "Active"), ("S", "Shutdown")],
            ),
        )
