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
        Activator = self.db.mock_model(
            model_name='Activator',
            db_table='sa_activator',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        self.db.add_column(
            "sa_managedobjectselector", "filter_activator",
            models.ForeignKey(Activator, verbose_name="Filter by Activator", null=True, blank=True)
        )
