# ----------------------------------------------------------------------
# default maintainer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if self.db.execute("SELECT COUNT(*) FROM peer_maintainer")[0][0] == 0:
            rir_id = self.db.execute("SELECT id FROM peer_rir LIMIT 1")[0][0]
            self.db.execute(
                "INSERT INTO peer_maintainer(maintainer,description,auth,rir_id) VALUES(%s,%s,%s,%s)",
                ["Default maintainer", "Please change to your maintainer", "NO AUTH", rir_id],
            )
