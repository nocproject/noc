# ----------------------------------------------------------------------
# Add ManagedObjectProfile.mac_collect_* fields
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
            "sa_managedobjectprofile", "mac_collect_all", models.BooleanField(default=False)
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "mac_collect_interface_profile",
            models.BooleanField(default=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile", "mac_collect_management", models.BooleanField(default=False)
        )
        self.db.add_column(
            "sa_managedobjectprofile", "mac_collect_multicast", models.BooleanField(default=False)
        )
        self.db.add_column(
            "sa_managedobjectprofile", "mac_collect_vcfilter", models.BooleanField(default=False)
        )
