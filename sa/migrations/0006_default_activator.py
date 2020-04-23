# ----------------------------------------------------------------------
# default activator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if self.db.execute("SELECT COUNT(*) FROM sa_activator")[0][0] == 0:
            self.db.execute(
                "INSERT INTO sa_activator(name,ip,is_active,auth) VALUES('default','127.0.0.1',true,'xxxxxxxxxxx')"
            )
