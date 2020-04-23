# ----------------------------------------------------------------------
# changes quarantine
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.fields import PickledField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Model 'Language'
        self.db.create_table(
            "main_changesquarantine",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("timestamp", models.DateTimeField("Timestamp", auto_now_add=True)),
                ("changes_type", models.CharField("Type", max_length=64)),
                ("subject", models.CharField("Subject", max_length=256)),
                ("data", PickledField("Data")),
            ),
        )

        self.db.create_table(
            "main_changesquarantinerule",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("is_active", models.BooleanField("Is Active", default=True)),
                ("changes_type", models.CharField("Type", max_length=64)),
                ("subject_re", models.CharField("Subject", max_length=256)),
                (
                    "action",
                    models.CharField(
                        "Action",
                        max_length=1,
                        choices=[("I", "Ignore"), ("A", "Accept"), ("Q", "Quarantine")],
                    ),
                ),
                ("description", models.TextField("Description", null=True, blank=True)),
            ),
        )
