# ---------------------------------------------------------------------
# Create ResourceState
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # ResourceState
        ResourceState = self.db.mock_model(
            model_name="ResourceState", db_table="main_resourcestate"
        )

        self.db.create_table(
            "main_resourcestate",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("description", models.TextField(null=True, blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_starting", models.BooleanField(default=True)),
                ("is_default", models.BooleanField(default=False)),
                ("is_provisioned", models.BooleanField(default=True)),
                (
                    "step_to",
                    models.ForeignKey(
                        ResourceState, blank=True, null=True, on_delete=models.CASCADE
                    ),
                ),
            ),
        )
