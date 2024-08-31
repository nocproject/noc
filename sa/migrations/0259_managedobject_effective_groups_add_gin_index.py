# ----------------------------------------------------------------------
# Create managedobject_effective_service_groups index.
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
            CREATE INDEX x_sa_managedobject_effective_service_groups_gin
            ON "sa_managedobject" USING GIN("effective_service_groups")
        """
        )
        self.db.execute(
            """
            CREATE INDEX x_sa_managedobject_effective_client_groups_gin
            ON "sa_managedobject" USING GIN("effective_client_groups")
        """
        )
        self.db.execute("DROP INDEX sa_managedobject_static_client_groups")
        self.db.execute("DROP INDEX sa_managedobject_static_service_groups")
