# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from south.db import db
from django.db import models
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.main.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    def forwards(self):
        User = db.mock_model(model_name="User",
            db_table="auth_user", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db.create_table("main_checkpoint", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("timestamp", models.DateTimeField(_("Timestamp"))),
            ("user", models.ForeignKey(User, verbose_name=_("User"), blank=True, null=True)),
            ("comment", models.CharField(_("Comment"), max_length=256)),
            ("private", models.BooleanField(_("Private"), default=False))
        ))
<<<<<<< HEAD

        db.send_create_signal("main", ["Checkpoint"])

=======
        
        db.send_create_signal("main", ["Checkpoint"])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_table("main_checkpoint")
