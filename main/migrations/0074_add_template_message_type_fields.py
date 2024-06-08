# ----------------------------------------------------------------------
# Add message_type to Template models
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
            "main_template", "is_system", models.BooleanField("SystemTemplate", default=False)
        )
        self.db.add_column(
            "main_template", "message_type", models.TextField("MessageType", blank=True, null=True)
        )
        self.db.add_column(
            "main_template",
            "context_data",
            models.TextField("ContextTestData", blank=True, null=True),
        )
        self.db.execute("ALTER TABLE main_template ALTER COLUMN body DROP NOT NULL")
