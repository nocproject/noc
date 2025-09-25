# ----------------------------------------------------------------------
# kbentrypreviewlog
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Mock Models
        KBEntry = self.db.mock_model(model_name="KBEntry", db_table="kb_kbentry")
        User = self.db.mock_model(model_name="User", db_table="auth_user")

        # Model "KBEntryPreviewLog"
        self.db.create_table(
            "kb_kbentrypreviewlog",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "kb_entry",
                    models.ForeignKey(KBEntry, verbose_name="KB Entry", on_delete=models.CASCADE),
                ),
                ("timestamp", models.DateTimeField("Timestamp", auto_now_add=True)),
                ("user", models.ForeignKey(User, verbose_name=User, on_delete=models.CASCADE)),
            ),
        )
