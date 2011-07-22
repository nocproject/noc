# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.main.models import *

class Migration:
    def forwards(self):
        User = db.mock_model(model_name="User",
            db_table="auth_user", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
        db.create_table("main_checkpoint", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("timestamp", models.DateTimeField(_("Timestamp"))),
            ("user", models.ForeignKey(User, verbose_name=_("User"), blank=True, null=True)),
            ("comment", models.CharField(_("Comment"), max_length=256)),
            ("private", models.BooleanField(_("Private"), default=False))
        ))
        
        db.send_create_signal("main", ["Checkpoint"])
    
    def backwards(self):
        db.delete_table("main_checkpoint")
