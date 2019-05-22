# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectselector vc_domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("ip", "0001_initial"), ("vc", "0001_initial")]

    def migrate(self):
        VRF = self.db.mock_model(
            model_name='VRF', db_table='ip_vrf', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField
        )
        VCDomain = self.db.mock_model(
            model_name='VCDomain',
            db_table='vc_vcdomain',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        self.db.add_column(
            "sa_managedobjectselector", "filter_vrf",
            models.ForeignKey(VRF, verbose_name="Filter by VRF", null=True, blank=True)
        )
        self.db.add_column(
            "sa_managedobjectselector", "filter_vc_domain",
            models.ForeignKey(VCDomain, verbose_name="Filter by VC Domain", null=True, blank=True)
        )
