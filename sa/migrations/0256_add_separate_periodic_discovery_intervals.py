# ---------------------------------------------------------------------
# Add Separate periodic discovery intervals to ManagedObject Profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    INTERVAL_COLUMNS = [
        "periodic_discovery_uptime_interval",
        "periodic_discovery_interface_status_interval",
        "periodic_discovery_mac_interval",
        "periodic_discovery_alarms_interval",
        "periodic_discovery_cpestatus_interval",
    ]

    def migrate(self):
        for n in self.INTERVAL_COLUMNS:
            self.db.add_column(
                "sa_managedobjectprofile",
                n,
                models.IntegerField(default=0),
            )
        # Set MAC Discovery
        self.db.execute(
            """
            UPDATE sa_managedobjectprofile
            SET periodic_discovery_mac_interval=box_discovery_interval, enable_periodic_discovery_mac = True
            WHERE enable_box_discovery_mac = True and enable_periodic_discovery_mac = False
        """
        )
        # Drop deprecated columns
        self.db.delete_column("sa_managedobjectprofile", "enable_box_discovery_mac")
        self.db.delete_column("sa_managedobjectprofile", "box_discovery_mac_filter_policy")
        self.db.delete_column("sa_managedobjectprofile", "enable_box_discovery_alarms")
        self.db.delete_column("sa_managedobjectprofile", "box_discovery_cpestatus_policy")
