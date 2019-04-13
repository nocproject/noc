# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject vrf
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    depends_on = [("ip", "0001_initial")]

    def forwards(self):
        VRF = db.mock_model(
            model_name="VRF", db_table="ip_vrf", db_tablespace="", pk_field_name="id", pk_field_type=models.AutoField
        )
        db.add_column("sa_managedobject", "vrf", models.ForeignKey(VRF, null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "vrf_id")
