# ----------------------------------------------------------------------
# extend dnszone name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        self.db.execute("ALTER TABLE dns_dnszone ALTER name TYPE VARCHAR(256)")
