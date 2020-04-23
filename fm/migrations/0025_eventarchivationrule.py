# ----------------------------------------------------------------------
# event archivation rule
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

        # Model 'EventArchivationRule'
        self.db.create_table(
            "fm_eventarchivationrule",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "event_class",
                    models.ForeignKey(
                        EventClass,
                        verbose_name="Event Class",
                        unique=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                ("ttl", models.IntegerField("Time To Live")),
                (
                    "ttl_measure",
                    models.CharField(
                        "Measure",
                        choices=[("s", "Seconds"), ("m", "Minutes"), ("h", "Hours"), ("d", "Days")],
                        default="h",
                        max_length=1,
                    ),
                ),
                (
                    "action",
                    models.CharField("Action", choices=[("D", "Drop")], default="D", max_length=1),
                ),
            ),
        )
