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
        db.create_table("main_shard", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), max_length=128, unique=True)),
            ("is_active", models.BooleanField(_("Is Active"), default=True)),
            ("description", models.TextField(_("Description"), null=True, blank=True)),
        ))
        db.send_create_signal("main", ["Shard"])
    
    def backwards(self):
        db.delete_table("main_shard")
    
