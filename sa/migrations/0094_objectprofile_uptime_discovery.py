# ----------------------------------------------------------------------
# managedobjectprofile uptime_discovery
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
            "sa_managedobjectprofile",
            "enable_uptime_discovery",
            models.BooleanField("Enable caps discovery", default=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "uptime_discovery_min_interval",
            models.IntegerField("Min. caps discovery interval", default=60),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "uptime_discovery_max_interval",
            models.IntegerField("Max. caps discovery interval", default=300),
        )
