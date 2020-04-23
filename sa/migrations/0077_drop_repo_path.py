# ----------------------------------------------------------------------
# drop repo path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("sa_managedobject", "is_configuration_managed")
        self.db.delete_column("sa_managedobject", "repo_path")
