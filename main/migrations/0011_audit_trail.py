# ----------------------------------------------------------------------
# audit trail
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("aaa", "0002_default_user")]

    def migrate(self):
        # Mock Models
        User = self.db.mock_model(model_name="User", db_table="auth_user")

        # Model 'AuditTrail'
        self.db.create_table(
            "main_audittrail",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("user", models.ForeignKey(User, verbose_name=User, on_delete=models.CASCADE)),
                ("timestamp", models.DateTimeField("Timestamp", auto_now=True)),
                ("model", models.CharField("Model", max_length=128)),
                ("db_table", models.CharField("Table", max_length=128)),
                (
                    "operation",
                    models.CharField(
                        "Operation",
                        max_length=1,
                        choices=[("C", "Create"), ("M", "Modify"), ("D", "Delete")],
                    ),
                ),
                ("subject", models.CharField("Subject", max_length=256)),
                ("body", models.TextField("Body")),
            ),
        )
