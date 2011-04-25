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
        ("main", "0034_default_shard"),
    ]
    def forwards(self):
        Shard = db.mock_model(model_name="Shard",
            db_table="main_shard", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
        db.add_column("sa_activator", "shard", models.ForeignKey(Shard, verbose_name=_("Shard"), null=True, blank=True))
    
    def backwards(self):
        db.delete_column("sa_activator", "shard_id")
