# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    depends_on = [
        ("ip", "0001_initial"),
        ("vc", "0001_initial")
    ]
    def forwards(self):
        VRF = db.mock_model(model_name='VRF',
            db_table='ip_vrf', db_tablespace='',
            pk_field_name='id', pk_field_type=models.AutoField)
        VCDomain = db.mock_model(model_name='VCDomain',
            db_table='vc_vcdomain', db_tablespace='',
            pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column(
            "sa_managedobjectselector", "filter_vrf",
            models.ForeignKey(VRF,
                verbose_name="Filter by VRF", null=True,
                blank=True))
        db.add_column(
            "sa_managedobjectselector", "filter_vc_domain",
            models.ForeignKey(VCDomain,
                verbose_name="Filter by VC Domain", null=True,
                blank=True))

    def backwards(self):
        db.delete_column("sa_managedobjectselector",
            "filter_vc_domain")
        db.delete_column("sa_managedobjectselector",
            "filter_vrf")
