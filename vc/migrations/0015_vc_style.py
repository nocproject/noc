# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc style
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0027_style")]

    def migrate(self):
        Style = self.db.mock_model(
            model_name="Style",
            db_table="main_style",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.add_column("vc_vcdomain", "style",
                           models.ForeignKey(Style, verbose_name="Style", null=True, blank=True))
        self.db.add_column("vc_vc", "style", models.ForeignKey(Style, verbose_name="Style", null=True, blank=True))
