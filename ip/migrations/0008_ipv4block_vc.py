# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    depends_on = (
        ("vc", "0001_initial"),
    )

    def forwards(self):
        VC = db.mock_model(model_name='VC', db_table='vc_vc',
                           db_tablespace='', pk_field_name='id',
                           pk_field_type=models.AutoField)
        db.add_column("ip_ipv4block", "vc",
                      models.ForeignKey(VC, verbose_name="VC",
                                        null=True, blank=True))

    def backwards(self):
        db.drop_column("ip_ipv4block", "vc_id")
