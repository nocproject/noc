# ----------------------------------------------------------------------
# restore useraccess
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute("DELETE FROM sa_useraccess")
        for id, name in self.db.execute(
            "SELECT id,name FROM sa_managedobjectselector WHERE name LIKE 'NOC_UA_%%'"
        ):
            uid, n = name[7:].split("_")
            self.db.execute(
                "INSERT INTO sa_useraccess(user_id,selector_id) VALUES(%s,%s)", [int(uid), id]
            )
