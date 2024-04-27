# ----------------------------------------------------------------------
# Add UUID in Template collections
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from django.db import models
import uuid

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column("main_template", "uuid", models.UUIDField(null=True))

        for id in self.db.execute("SELECT id FROM main_template"):
            u = str(uuid.uuid4())
            self.db.execute(
                "UPDATE main_template SET uuid=%s WHERE id =%s and uuid IS NULL", [u, id]
            )
