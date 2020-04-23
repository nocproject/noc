# ----------------------------------------------------------------------
# DNSZone.type field
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
            "dns_dnszone",
            "type",
            models.CharField(
                "Type",
                max_length=1,
                null=False,
                blank=False,
                default="F",
                choices=[("F", "Forward"), ("4", "Reverse IPv4"), ("6", "Reverse IPv6")],
            ),
        )
        self.db.execute("UPDATE dns_dnszone SET type = '4' WHERE name ILIKE '%%.in-addr.arpa'")
        self.db.execute(
            "UPDATE dns_dnszone SET type = '6' WHERE name ILIKE '%%.ip6.int' OR name ILIKE '.ip6.arpa'"
        )
