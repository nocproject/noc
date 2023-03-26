# ----------------------------------------------------------------------
# Remove effective_labels on ManagedObjectProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("sa_managedobjectprofile", "effective_labels")
