# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *

class Migration:
    depends_on=[
        ("main", "0035_prefix_table"),
    ]
    def forwards(self):
        Shard = db.mock_model(model_name="Shard",
            db_table="main_shard", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        PrefixTable = db.mock_model(model_name="PrefixTable",
            db_table="main_prefixtable", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        db.add_column("sa_managedobjectselector", "filter_prefix",
            models.ForeignKey(PrefixTable, verbose_name="Filter by Prefix Table",
                null=True, blank=True))
        db.add_column("sa_managedobjectselector", "filter_shard",
            models.ForeignKey(Shard, verbose_name="Filter by shard",
                null=True, blank=True))
    
    def backwards(self):
        db.delete_column("sa_managedobjectselector", "filter_shard_id")
        db.delete_column("sa_managedobjectselector", "filter_prefix_id")
    
