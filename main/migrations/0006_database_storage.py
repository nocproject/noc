# ----------------------------------------------------------------------
# databasestorage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.fields import BinaryField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Model 'DatabaseStorage'
        self.db.create_table(
            "main_databasestorage",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=256, unique=True)),
                ("data", BinaryField("Data")),
                ("size", models.IntegerField("Size")),
                ("mtime", models.DateTimeField("MTime")),
            ),
        )
