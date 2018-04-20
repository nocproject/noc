# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
from south.db import db
from django.db import models

class Migration:
    depends_on=[
        ("main", "0034_default_shard"),
    ]
    def forwards(self):
        Shard = db.mock_model(model_name="Shard",
            db_table="main_shard", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
<<<<<<< HEAD

        db.add_column("sa_activator", "shard", models.ForeignKey(Shard, verbose_name=_("Shard"), null=True, blank=True))

=======
        
        db.add_column("sa_activator", "shard", models.ForeignKey(Shard, verbose_name=_("Shard"), null=True, blank=True))
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_column("sa_activator", "shard_id")
