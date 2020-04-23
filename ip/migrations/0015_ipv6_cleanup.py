# ----------------------------------------------------------------------
# ipv6 cleanup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # VRFGroup
        self.db.delete_column("ip_vrfgroup", "unique_addresses")
        # Delete obsolete tables
        self.db.delete_table("ip_ipv4block")
        self.db.delete_table("ip_ipv4address")
        self.db.delete_table("ip_ipv4blockaccess")
        self.db.delete_table("ip_ipv4blockbookmark")
        self.db.delete_table("ip_ipv4addressrange")
        self.db.execute("DROP FUNCTION free_ip(INTEGER,CIDR)")
