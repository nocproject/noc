# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vcdomainprovisioningconfig filter
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
        VCFilter = self.db.mock_model(
            model_name='VCFilter',
            db_table='vc_vcfilter',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        self.db.add_column(
            "vc_vcdomainprovisioningconfig", "vc_filter",
            models.ForeignKey(VCFilter, verbose_name="VC Filter", null=True, blank=True)
        )
