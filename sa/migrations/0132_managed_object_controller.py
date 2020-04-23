# ----------------------------------------------------------------------
# managedobject controller
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
        ManagedObject = self.db.mock_model(model_name="ManagedObject", db_table="sa_managedobject")

        self.db.add_column(
            "sa_managedobject",
            "controller",
            models.ForeignKey(
                ManagedObject,
                verbose_name="Controller",
                blank=True,
                null=True,
                on_delete=models.CASCADE,
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "last_seen",
            models.DateTimeField("Last Seen", blank=True, null=True),
        )
