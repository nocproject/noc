# ----------------------------------------------------------------------
# drop groups and fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Drop groups and fields
        self.db.delete_column("cm_objectnotify", "group_id")
