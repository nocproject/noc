# ----------------------------------------------------------------------
# object notify drop emails
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("cm_objectnotify", "emails")
        self.db.execute(
            "ALTER TABLE cm_objectnotify ALTER COLUMN notification_group_id SET NOT NULL"
        )
