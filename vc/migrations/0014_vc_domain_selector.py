# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc domain selector
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
        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.add_column(
            "vc_vcdomain", "selector",
            models.ForeignKey(ManagedObjectSelector, verbose_name="Selector", null=True, blank=True)
        )
