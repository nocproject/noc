# ----------------------------------------------------------------------
# managedobjectprofile weight
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
            "sa_managedobjectprofile", "weight", models.IntegerField("Alarm weight", default=0)
        )
        self.db.delete_column("sa_managedobjectprofile", "check_link_interval")
        self.db.delete_column("sa_managedobjectprofile", "down_severity")
