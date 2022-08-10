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
    def migrate(self):
        self.db.add_column(
            "ip_address",
            "state_changed",
            models.DateTimeField("State Changed", blank=True, null=True),
        )
        self.db.add_column(
            "ip_address",
            "expired",
            models.DateTimeField("Expired", blank=True, null=True),
        )
        self.db.add_column(
            "ip_address",
            "last_seen",
            models.DateTimeField("Last Seen", blank=True, null=True),
        )
        self.db.add_column(
            "ip_address",
            "first_discovered",
            models.DateTimeField("First Discovered", blank=True, null=True),
        )

        self.db.add_column(
            "ip_prefix",
            "state_changed",
            models.DateTimeField("State Changed", blank=True, null=True),
        )
        self.db.add_column(
            "ip_prefix",
            "expired",
            models.DateTimeField("Expired", blank=True, null=True),
        )
        self.db.add_column(
            "ip_prefix",
            "last_seen",
            models.DateTimeField("Last Seen", blank=True, null=True),
        )
        self.db.add_column(
            "ip_prefix",
            "first_discovered",
            models.DateTimeField("First Discovered", blank=True, null=True),
        )

        self.db.add_column(
            "ip_vrf",
            "state_changed",
            models.DateTimeField("State Changed", blank=True, null=True),
        )
        self.db.add_column(
            "ip_vrf",
            "expired",
            models.DateTimeField("Expired", blank=True, null=True),
        )
        self.db.add_column(
            "ip_vrf",
            "last_seen",
            models.DateTimeField("Last Seen", blank=True, null=True),
        )
        self.db.add_column(
            "ip_vrf",
            "first_discovered",
            models.DateTimeField("First Discovered", blank=True, null=True),
        )
