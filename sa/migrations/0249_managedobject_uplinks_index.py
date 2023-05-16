# ----------------------------------------------------------------------
# Create managedobject_uplinks index.
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
            CREATE INDEX x_sa_managedobject_uplinks
            ON "sa_managedobject" USING GIN("uplinks")
        """
        )
        # Remove config field from diagnostics
        self.db.execute(
            """
            UPDATE sa_managedobject
            SET diagnostics = '{}'::jsonb
            WHERE diagnostics -> 'SA' ? 'config'
        """
        )
