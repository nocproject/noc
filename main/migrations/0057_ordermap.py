# ----------------------------------------------------------------------
#  OrderMap
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
        # Model 'Color'
        self.db.create_table(
            "main_ordermap",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("model", models.CharField("Model", max_length=64)),
                ("ref_id", models.CharField("Ref ID", max_length=24)),
                ("name", models.CharField("Name", max_length=256)),
            ),
        )
        self.db.create_index("main_ordermap", ["model", "ref_id"], unique=True)
