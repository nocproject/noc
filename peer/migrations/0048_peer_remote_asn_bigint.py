# ----------------------------------------------------------------------
# Change Migrate Peer.remote_asn type to bigint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC module
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute("ALTER TABLE peer_peer ALTER remote_asn TYPE BIGINT")
        self.db.execute("ALTER TABLE peer_peer ALTER remote_asn DROP NOT NULL")
