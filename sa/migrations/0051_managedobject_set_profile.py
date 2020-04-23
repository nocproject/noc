# ----------------------------------------------------------------------
# managedobject set profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        r = self.db.execute("SELECT id FROM sa_managedobjectprofile WHERE name='default'")
        p_id = r[0][0]
        self.db.execute("UPDATE sa_managedobject SET object_profile_id = %s", [p_id])
