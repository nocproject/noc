# ----------------------------------------------------------------------
# community type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

NAMES = ["Other Normal", "Other Extended"]


class Migration(BaseMigration):
    def migrate(self):
        for n in NAMES:
            if (
                self.db.execute("SELECT COUNT(*) FROM peer_communitytype WHERE name=%s", [n])[0][0]
                == 0
            ):
                self.db.execute("INSERT INTO peer_communitytype(name) VALUES(%s)", [n])
