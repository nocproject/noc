# ----------------------------------------------------------------------
# Extend ip.Address, ip.Prefix and ip.VRF models by status TTL fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def add_column(self, table: str, column: str, column_title: str):
        self.db.add_column(
            table,
            column,
            models.DateTimeField(column_title, blank=True, null=True),
        )

    def migrate(self):
        tables = ("ip_address", "ip_prefix", "ip_vrf")
        columns = {
            "state_changed": "State Changed",
            "expired": "Expired",
            "last_seen": "Last Seen",
            "first_discovered": "First Discovered",
        }
        for table in tables:
            for column, column_title in columns.items():
                self.add_column(table, column, column_title)
