# ----------------------------------------------------------------------
# Create affected_maintenances index.
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            """
            CREATE INDEX sa_managedobject_affected_maintenances_idx
            ON "sa_managedobject" USING GIN("affected_maintenances")
        """
        )
