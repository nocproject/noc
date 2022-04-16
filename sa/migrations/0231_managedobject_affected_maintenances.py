# ----------------------------------------------------------------------
# Migrate ManagedObject Caps Field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
            "affected_maintenances",
            models.JSONField("Maintenance Items", null=True, blank=True, default=lambda: "{}"),
        )
