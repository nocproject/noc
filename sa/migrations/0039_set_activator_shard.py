# ----------------------------------------------------------------------
# set activator shard
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    NAME = "default"

    def migrate(self):
        shard_id = self.db.execute("SELECT id FROM main_shard WHERE name=%s", [self.NAME])[0][0]
        self.db.execute("UPDATE sa_activator SET shard_id=%s", [shard_id])
