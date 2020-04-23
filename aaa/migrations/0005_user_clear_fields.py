# ----------------------------------------------------------------------
# Remove unused legacy fields from User model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if self.db.has_column("auth_user", "is_staff"):
            self.db.delete_column("auth_user", "is_staff")
