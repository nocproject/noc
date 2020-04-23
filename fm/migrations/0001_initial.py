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
    def migrate(self):

        # Model 'MIB'
        self.db.create_table(
            "fm_mib",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("description", models.TextField("Description", blank=True, null=True)),
                ("last_updated", models.DateTimeField("Last Updated")),
                ("uploaded", models.DateTimeField("Uploaded")),
            ),
        )

        # Mock Models
        MIB = self.db.mock_model(model_name="MIB", db_table="fm_mib")

        # Model 'MIBData'
        self.db.create_table(
            "fm_mibdata",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("mib", models.ForeignKey(MIB, verbose_name=MIB, on_delete=models.CASCADE)),
                ("oid", models.CharField("OID", max_length=128, unique=True)),
                ("name", models.CharField("Name", max_length=128, unique=True)),
                ("description", models.TextField("Description", blank=True, null=True)),
            ),
        )
