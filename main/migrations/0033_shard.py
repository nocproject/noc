# ----------------------------------------------------------------------
# shard
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
        self.db.create_table(
            "main_shard",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=128, unique=True)),
                ("is_active", models.BooleanField("Is Active", default=True)),
                ("description", models.TextField("Description", null=True, blank=True)),
            ),
        )
