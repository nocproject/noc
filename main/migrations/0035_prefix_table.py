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
        db.create_table("main_prefixtable", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), max_length=128, unique=True)),
            ("description", models.TextField(_("Description"), null=True, blank=True)),
        ))
        
        PrefixTable = db.mock_model(model_name="PrefixTable",
            db_table="main_prefixtable", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
        db.create_table("main_prefixtableprefix", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("table", models.ForeignKey(PrefixTable, verbose_name = _("Prefix Table"))),
            ("afi", models.CharField(_("Address Family"),max_length=1,
                    choices=[("4", _("IPv4")), ("6", _("IPv6"))])),
            ("prefix", CIDRField(_("Prefix")))
        ))
        
        db.send_create_signal("main", ["PrefixTable", "PrefixTablePrefix"])
    
    def backwards(self):
        db.delete_table("main_prefixtable")
        db.delete_table("main_prefixtableprefix")
    
