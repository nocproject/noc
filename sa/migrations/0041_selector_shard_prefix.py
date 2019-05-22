# ----------------------------------------------------------------------
# selector shard prefix
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [
        ("main", "0035_prefix_table"),
    ]

    def migrate(self):
        Shard = self.db.mock_model(
            model_name="Shard",
            db_table="main_shard",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        PrefixTable = self.db.mock_model(
            model_name="PrefixTable",
            db_table="main_prefixtable",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.add_column(
            "sa_managedobjectselector", "filter_prefix",
            models.ForeignKey(PrefixTable, verbose_name="Filter by Prefix Table", null=True, blank=True)
        )
        self.db.add_column(
            "sa_managedobjectselector", "filter_shard",
            models.ForeignKey(Shard, verbose_name="Filter by shard", null=True, blank=True)
        )
