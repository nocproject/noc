# ----------------------------------------------------------------------
# Migrate ManagedObject diagnostics state
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobject",
            "mappings",
            models.JSONField("Remote System mappings", null=True, blank=True, default=lambda: "[]"),
        )
        self.db.create_index("sa_managedobject", ["remote_system", "remote_id"], unique=False)
        self.db.execute(
            """
            CREATE INDEX sa_managedobject_remote_mappings_idx
            ON "sa_managedobject" USING GIN("mappings" jsonb_path_ops)
        """
        )
