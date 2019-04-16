# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# activator shard
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
    depends_on = [
        ("main", "0034_default_shard"),
    ]

    def forwards(self):
        Shard = db.mock_model(
            model_name="Shard",
            db_table="main_shard",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        db.add_column("sa_activator", "shard", models.ForeignKey(Shard, verbose_name="Shard", null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_activator", "shard_id")
