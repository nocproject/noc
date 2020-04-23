# ----------------------------------------------------------------------
# drop activator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0033_shard")]

    def migrate(self):
        self.db.delete_column("sa_managedobjectselector", "filter_activator_id")
        self.db.delete_table("sa_activator")
        self.db.delete_table("sa_collector")
        self.db.delete_table("main_shard")
