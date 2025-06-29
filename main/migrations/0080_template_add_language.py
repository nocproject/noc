# ----------------------------------------------------------------------
# Template add language
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "main_template",
            "language",
            models.CharField("Language", max_length=16, null=True, blank=True),
        )
