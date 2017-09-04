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
            ('scope', models.CharField("Scope", max_length=64)),
            ('scope_id', models.CharField("ID", max_length=24)),
            ('name', models.CharField("Name", max_length=256))
        ))
        db.create_index("main_ordermap", ["scope", "scope_id"], unique=True)

    def backwards(self):
        db.delete_table("main_ordermap")
