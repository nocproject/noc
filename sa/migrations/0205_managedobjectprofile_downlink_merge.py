# ----------------------------------------------------------------------
# ManagedObjectProfile xRCA settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
            "enable_rca_downlink_merge",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "rca_downlink_merge_window",
            models.IntegerField(default=120),
        )
