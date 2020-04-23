# ----------------------------------------------------------------------
# kb_entry_yattachment
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

        # Model "KBEntryAttachment"
        self.db.create_table(
            "kb_kbentryattachment",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "kb_entry",
                    models.ForeignKey(KBEntry, verbose_name="KB Entry", on_delete=models.CASCADE),
                ),
                ("name", models.CharField("Name", max_length=256)),
                (
                    "description",
                    models.CharField("Description", max_length=256, null=True, blank=True),
                ),
                ("is_hidden", models.BooleanField("Is Hidden", default=False)),
                ("file", models.FileField("File")),
            ),
        )
        self.db.create_index("kb_kbentryattachment", ["kb_entry_id", "name"], unique=True)
