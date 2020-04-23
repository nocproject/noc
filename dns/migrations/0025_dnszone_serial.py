# ----------------------------------------------------------------------
# dnszone serial
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute("ALTER TABLE dns_dnszone ALTER serial DROP DEFAULT")
        self.db.execute("ALTER TABLE dns_dnszone ALTER serial TYPE INTEGER USING serial::integer")
        self.db.execute("ALTER TABLE dns_dnszone ALTER serial SET DEFAULT 0")
        self.db.execute("ALTER TABLE dns_dnszone ALTER serial SET NOT NULL")
