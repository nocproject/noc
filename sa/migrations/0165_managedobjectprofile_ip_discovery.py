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
            "sa_managedobjectprofile",
            "enable_box_discovery_vrf",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address",
            models.BooleanField(default=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address_interface",
            models.BooleanField(default=False),
        )
        # self.db.add_column(
        #     "sa_managedobjectprofile",
        #     "enable_box_discovery_prefix",
        #     models.BooleanField(default=False)
        # )
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_prefix_interface",
            models.BooleanField(default=False),
        )
