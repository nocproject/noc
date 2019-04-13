# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc domain selector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
# NOC modules
from django.db import models


class Migration(object):
    def forwards(self):
        ManagedObjectSelector = db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        db.add_column(
            "vc_vcdomain", "selector",
            models.ForeignKey(ManagedObjectSelector, verbose_name="Selector", null=True, blank=True)
        )

    def backwards(self):
        db.drop_column("vc_vcdomain", "selector")
