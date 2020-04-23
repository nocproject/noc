# ---------------------------------------------------------------------
# Set .state NOT NULL
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Get default resource state id
        r = self.db.execute("SELECT id FROM main_resourcestate WHERE is_default = true")
        if len(r) != 1:
            raise Exception("Cannot get default state")
        ds = r[0][0]
        # Set up default state
        self.db.execute("UPDATE ip_vrf SET state_id = %s", [ds])
        self.db.execute("UPDATE ip_prefix SET state_id = %s", [ds])
        self.db.execute("UPDATE ip_address SET state_id = %s", [ds])
