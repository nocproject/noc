# ----------------------------------------------------------------------
# drop config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0077_drop_repo_path")]

    def migrate(self):
        self.db.delete_table("cm_config")
