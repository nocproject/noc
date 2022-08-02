# ----------------------------------------------------------------------
# Migrate ManagedObject diagnostics state
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
            "diagnostics",
            models.JSONField("Diagnostic check items", null=True, blank=True, default=lambda: "{}"),
        )
