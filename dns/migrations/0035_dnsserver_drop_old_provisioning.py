# ----------------------------------------------------------------------
# dnsserver drop old provisioning
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        for c in ["generator_name", "location", "provisioning", "autozones_path"]:
            self.db.delete_column("dns_dnsserver", c)
