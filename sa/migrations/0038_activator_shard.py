# ----------------------------------------------------------------------
# activator shard
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0034_default_shard")]

    def migrate(self):
        Shard = self.db.mock_model(model_name="Shard", db_table="main_shard")

        self.db.add_column(
            "sa_activator",
            "shard",
            models.ForeignKey(
                Shard, verbose_name="Shard", null=True, blank=True, on_delete=models.CASCADE
            ),
        )
