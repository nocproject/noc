# ----------------------------------------------------------------------
# inv prefix_discovery notification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if (
            self.db.execute(
                "SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",
                ["inv.prefix_discovery"],
            )[0][0]
            == 0
        ):
            self.db.execute(
                "INSERT INTO main_systemnotification(name) VALUES(%s)", ["inv.prefix_discovery"]
            )
