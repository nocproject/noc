# ---------------------------------------------------------------------
# Cleanup SubInterface's is_* indexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        c = self.mongo_db.noc.subinterfaces
        for i in ("is_ipv4_1", "is_ipv6_1", "is_bridge_1"):
            try:
                c.drop_index(i)
            except Exception:
                pass
