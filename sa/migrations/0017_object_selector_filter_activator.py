# ----------------------------------------------------------------------
# object selector filter activator
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
        Activator = self.db.mock_model(model_name="Activator", db_table="sa_activator")
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_activator",
            models.ForeignKey(
                Activator,
                verbose_name="Filter by Activator",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
