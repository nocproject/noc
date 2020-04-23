# ----------------------------------------------------------------------
# activator drop ip
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("sa_activator", "ip")
        self.db.delete_column("sa_activator", "to_ip")
        self.db.execute("ALTER TABLE sa_activator ALTER prefix_table_id SET NOT NULL")
