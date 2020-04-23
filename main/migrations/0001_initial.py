# ----------------------------------------------------------------------
# initial
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create plpgsql language when necessary
        if self.db.execute("SELECT COUNT(*) FROM pg_language WHERE lanname='plpgsql'")[0][0] == 0:
            self.db.execute("CREATE LANGUAGE plpgsql")
