# ----------------------------------------------------------------------
# kb_entry_template
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
        Language = self.db.mock_model(model_name="Language", db_table="main_language")

        # Model "KBEntryTemplate"
        self.db.create_table(
            "kb_kbentrytemplate",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=128, unique=True)),
                ("subject", models.CharField("Subject", max_length=256)),
                ("body", models.TextField("Body")),
                (
                    "language",
                    models.ForeignKey(
                        Language,
                        verbose_name=Language,
                        limit_choices_to={"is_active": True},
                        on_delete=models.CASCADE,
                    ),
                ),
                ("markup_language", models.CharField("Markup Language", max_length="16")),
            ),
        )
        # Mock Models
        KBEntryTemplate = self.db.mock_model(
            model_name="KBEntryTemplate", db_table="kb_kbentrytemplate"
        )
        KBCategory = self.db.mock_model(model_name="KBCategory", db_table="kb_kbcategory")

        # M2M field "KBEntryTemplate.categories"
        self.db.create_table(
            "kb_kbentrytemplate_categories",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "kbentrytemplate",
                    models.ForeignKey(KBEntryTemplate, null=False, on_delete=models.CASCADE),
                ),
                ("kbcategory", models.ForeignKey(KBCategory, null=False, on_delete=models.CASCADE)),
            ),
        )
