# ----------------------------------------------------------------------
# managedobjectprofile check_link interval
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
        # Alter sa_managedobjectprofile
        self.db.add_column(
            "sa_managedobjectprofile",
            "check_link_interval",
            models.CharField(
                "check_link interval", max_length=256, blank=True, null=True, default=",60"
            ),
        )
