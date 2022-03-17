# ----------------------------------------------------------------------
# extend description
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute("ALTER TABLE peer_as ALTER description TYPE TEXT")
        self.db.execute("ALTER TABLE peer_community ALTER description TYPE TEXT")
        self.db.execute("ALTER TABLE peer_peer ALTER description TYPE TEXT")
