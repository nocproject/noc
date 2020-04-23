# ----------------------------------------------------------------------
# managedobjectprofile ping
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
            "ping_policy",
            models.CharField(
                "Ping check policy",
                max_length=1,
                choices=[("f", "First Success"), ("a", "All Successes")],
                default="f",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "ping_size",
            models.IntegerField("Ping packet size", default=64),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "ping_count",
            models.IntegerField("Ping packets count", default=3),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "ping_timeout_ms",
            models.IntegerField("Ping timeout (ms)", default=1000),
        )
