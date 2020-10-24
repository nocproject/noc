# ----------------------------------------------------------------------
# mib dependency
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
        MIB = self.db.mock_model(model_name="MIB", db_table="fm_mib")

        # Model 'MIBDependency'
        self.db.create_table(
            "fm_mibdependency",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("mib", models.ForeignKey(MIB, verbose_name=MIB, on_delete=models.CASCADE)),
                (
                    "requires_mib",
                    models.ForeignKey(
                        MIB,
                        verbose_name="Requires MIB",
                        related_name="requiredbymib_set",
                        on_delete=models.CASCADE,
                    ),
                ),
            ),
        )
        self.db.create_index("fm_mibdependency", ["mib_id", "requires_mib_id"], unique=True)
