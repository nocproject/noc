# ----------------------------------------------------------------------
# drop cache tables
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_table("peer_prefixlistcache")
        self.db.delete_table("peer_whoiscache")
        self.db.delete_table("peer_whoislookup")
        self.db.delete_table("peer_whoisdatabase")
