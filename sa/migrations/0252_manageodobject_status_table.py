# ----------------------------------------------------------------------
# Create ManagedObject status table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Model 'Task'
        self.db.create_table(
            "sa_objectstatus",
            (
                ("managed_object", models.IntegerField("Task", unique=True, primary_key=True)),
                ("last", models.DateTimeField("Last update Time", auto_now_add=True)),
                ("status", models.BooleanField("Status")),
            ),
        )
        # Migration ObjectStatus
