# ----------------------------------------------------------------------
# managedobjectprofile id discovery
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
            "enable_id_discovery",
            models.BooleanField("Enable ID discovery", default=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "id_discovery_min_interval",
            models.IntegerField("Min. ID discovery interval", default=600),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "id_discovery_max_interval",
            models.IntegerField("Max. ID discovery interval", default=86400),
        )
