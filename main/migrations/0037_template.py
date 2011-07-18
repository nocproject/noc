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
        db.create_table("main_template", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), unique=True, max_length=128)),
            ("subject", models.TextField(_("Subject"))),
            ("body", models.TextField(_("Body"))),
        ))
        
        Template = db.mock_model(model_name="Template",
            db_table="main_template", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
        db.create_table("main_systemtemplate", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), max_length=64, unique=True)),
            ("description", models.TextField(_("Description"), null=True, blank=True)),
            ("template", models.ForeignKey(Template, verbose_name=_("Template"))),
        ))
        
        db.send_create_signal("main", ["Template", "SystemTemplate"])
    
    def backwards(self):
        db.delete_table("main_systemtemplate")
        db.delete_table("main_template")
