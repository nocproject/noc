# ----------------------------------------------------------------------
# default shard
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    NAME = "default"

    def migrate(self):
        if self.db.execute("SELECT COUNT(*) FROM main_shard WHERE name=%s", [self.NAME])[0][0] == 0:
            self.db.execute(
                "INSERT INTO main_shard(name, is_active, description) VALUES(%s, %s, %s)",
                [self.NAME, True, "Default shard"],
            )
