# ----------------------------------------------------------------------
# refbook
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

        # Model 'RefBook'
        self.db.create_table(
            "main_refbook",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=128, unique=True)),
                (
                    "language",
                    models.ForeignKey(Language, verbose_name=Language, on_delete=models.CASCADE),
                ),
                ("description", models.TextField("Description", blank=True, null=True)),
                ("is_enabled", models.BooleanField("Is Enabled", default=False)),
                ("is_builtin", models.BooleanField("Is Builtin", default=False)),
                (
                    "downloader",
                    models.CharField("Downloader", max_length=64, blank=True, null=True),
                ),
                (
                    "download_url",
                    models.CharField("Download URL", max_length=256, null=True, blank=True),
                ),
                ("last_updated", models.DateTimeField("Last Updated", blank=True, null=True)),
                ("next_update", models.DateTimeField("Next Update", blank=True, null=True)),
                ("refresh_interval", models.IntegerField("Refresh Interval (days)", default=0)),
            ),
        )

        # Mock Models
        RefBook = self.db.mock_model(model_name="RefBook", db_table="main_refbook")

        # Model 'RefBookField'
        self.db.create_table(
            "main_refbookfield",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "ref_book",
                    models.ForeignKey(RefBook, verbose_name="Ref Book", on_delete=models.CASCADE),
                ),
                ("name", models.CharField("Name", max_length="64")),
                ("order", models.IntegerField("Order")),
                ("is_required", models.BooleanField("Is Required", default=True)),
                ("description", models.TextField("Description", blank=True, null=True)),
                (
                    "search_method",
                    models.CharField("Search Method", max_length=64, blank=True, null=True),
                ),
            ),
        )
        self.db.create_index("main_refbookfield", ["ref_book_id", "order"], unique=True)

        self.db.create_index("main_refbookfield", ["ref_book_id", "name"], unique=True)

        # Mock Models
        RefBook = self.db.mock_model(model_name="RefBook", db_table="main_refbook")
        RefBookField = self.db.mock_model(model_name="RefBookField", db_table="main_refbookfield")

        # Model 'RefBookData'
        self.db.create_table(
            "main_refbookdata",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "ref_book",
                    models.ForeignKey(RefBook, verbose_name="Ref Book", on_delete=models.CASCADE),
                ),
                ("record_id", models.IntegerField("ID")),
                (
                    "field",
                    models.ForeignKey(RefBookField, verbose_name="Field", on_delete=models.CASCADE),
                ),
                ("value", models.TextField("Value", null=True, blank=True)),
            ),
        )
        self.db.create_index(
            "main_refbookdata", ["ref_book_id", "record_id", "field_id"], unique=True
        )
