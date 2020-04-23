# ----------------------------------------------------------------------
# Make peer.asn_id nullable
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        rows = self.db.execute("SELECT id FROM peer_as WHERE asn = 0")
        as_id = rows[0][0]
        self.db.execute("ALTER TABLE ip_prefix ALTER asn_id DROP NOT NULL")
        self.db.execute(
            """
            UPDATE ip_prefix
            SET asn_id = NULL
            WHERE asn_id = %s
        """,
            [as_id],
        )
