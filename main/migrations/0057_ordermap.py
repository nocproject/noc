# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  OrderMap
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# encoding: utf-8
from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        # Model 'Color'
        db.create_table('main_ordermap', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True,
                                    auto_created=True)),
            ('model', models.CharField("Model", max_length=64)),
            ('ref_id', models.CharField("Ref ID", max_length=24)),
            ('name', models.CharField("Name", max_length=256))
        ))
        db.create_index("main_ordermap", ["model", "ref_id"], unique=True)

    def backwards(self):
        db.delete_table("main_ordermap")
