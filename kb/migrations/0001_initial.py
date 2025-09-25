# ----------------------------------------------------------------------
# initial
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0004_language")]

    def migrate(self):
        # Model "KBCategory"
        self.db.create_table(
            "kb_kbcategory",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
            ),
        )

        # Mock Models
        Language = self.db.mock_model(model_name="Language", db_table="main_language")

        # Model "KBEntry"
        self.db.create_table(
            "kb_kbentry",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("subject", models.CharField("Subject", max_length=256)),
                ("body", models.TextField("Body")),
                (
                    "language",
                    models.ForeignKey(Language, verbose_name=Language, on_delete=models.CASCADE),
                ),
                ("markup_language", models.CharField("Markup Language", max_length="16")),
            ),
        )
        # Mock Models
        KBEntry = self.db.mock_model(model_name="KBEntry", db_table="kb_kbentry")
        KBCategory = self.db.mock_model(model_name="KBCategory", db_table="kb_kbcategory")

        # M2M field "KBEntry.categories"
        self.db.create_table(
            "kb_kbentry_categories",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("kbentry", models.ForeignKey(KBEntry, null=False, on_delete=models.CASCADE)),
                ("kbcategory", models.ForeignKey(KBCategory, null=False, on_delete=models.CASCADE)),
            ),
        )

        # Mock Models
        KBEntry = self.db.mock_model(model_name="KBEntry", db_table="kb_kbentry")
        User = self.db.mock_model(model_name="User", db_table="auth_user")

        # Model "KBEntryHistory"
        self.db.create_table(
            "kb_kbentryhistory",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "kb_entry",
                    models.ForeignKey(KBEntry, verbose_name="KB Entry", on_delete=models.CASCADE),
                ),
                ("timestamp", models.DateTimeField("Timestamp", auto_now_add=True)),
                ("user", models.ForeignKey(User, verbose_name=User, on_delete=models.CASCADE)),
                ("diff", models.TextField("Diff")),
            ),
        )
