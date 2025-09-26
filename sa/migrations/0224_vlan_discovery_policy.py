# ----------------------------------------------------------------------
# managedobjectprofile vlan discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
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
            "vlan_vlandb_discovery",
            models.CharField(
                "VLAN DB Discovery Policy",
                max_length=1,
                choices=[
                    ("D", "Disable"),
                    ("S", "Status Only"),
                    ("V", "VLAN Sync"),
                ],
                default="D",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "vlan_interface_discovery",
            models.CharField(
                "VLAN Interface Discovery Policy",
                max_length=1,
                choices=[
                    ("D", "Disable"),
                    ("S", "Status Only"),
                    ("V", "VLAN Sync"),
                ],
                default="D",
            ),
        )
        self.db.execute(
            """
            UPDATE sa_managedobjectprofile
            SET vlan_vlandb_discovery = 'V'
            WHERE enable_box_discovery_vlan = True
            """
        )
        # Drop enable_box_discovery_vlan column
        self.db.delete_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_vlan",
        )
