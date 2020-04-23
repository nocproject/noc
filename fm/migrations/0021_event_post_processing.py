# ----------------------------------------------------------------------
# event post processing
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
        EventClass = self.db.mock_model(model_name="EventClass", db_table="fm_eventclass")
        EventPriority = self.db.mock_model(model_name="EventPriority", db_table="fm_eventpriority")
        EventCategory = self.db.mock_model(model_name="EventCategory", db_table="fm_eventcategory")

        # Model 'EventPostProcessingRule'
        self.db.create_table(
            "fm_eventpostprocessingrule",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "event_class",
                    models.ForeignKey(
                        EventClass, verbose_name="Event Class", on_delete=models.CASCADE
                    ),
                ),
                ("name", models.CharField("Name", max_length=64)),
                ("preference", models.IntegerField("Preference", default=1000)),
                ("is_active", models.BooleanField("Is Active", default=True)),
                ("description", models.TextField("Description", blank=True, null=True)),
                (
                    "change_priority",
                    models.ForeignKey(
                        EventPriority,
                        verbose_name="Change Priority to",
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "change_category",
                    models.ForeignKey(
                        EventCategory,
                        verbose_name="Change Category to",
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        "Action",
                        max_length=1,
                        choices=[("A", "Make Active"), ("C", "Close"), ("D", "Drop")],
                        default="A",
                    ),
                ),
            ),
        )

        # Mock Models
        EventPostProcessingRule = self.db.mock_model(
            model_name="EventPostProcessingRule", db_table="fm_eventpostprocessingrule"
        )

        # Model 'EventPostProcessingRE'
        self.db.create_table(
            "fm_eventpostprocessingre",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "rule",
                    models.ForeignKey(
                        EventPostProcessingRule,
                        verbose_name="Event Post-Processing Rule",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("var_re", models.CharField("Var RE", max_length=256)),
                ("value_re", models.CharField("Value RE", max_length=256)),
            ),
        )
