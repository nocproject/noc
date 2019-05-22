# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ipv4block vc
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    depends_on = (("vc", "0001_initial"),)

    def migrate(self):
        VC = self.db.mock_model(
            model_name='VC', db_table='vc_vc', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField
        )
        self.db.add_column("ip_ipv4block", "vc", models.ForeignKey(VC, verbose_name="VC", null=True, blank=True))
