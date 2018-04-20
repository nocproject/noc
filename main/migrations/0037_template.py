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
        db.create_table("main_template", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), unique=True, max_length=128)),
            ("subject", models.TextField(_("Subject"))),
            ("body", models.TextField(_("Body"))),
        ))
<<<<<<< HEAD

        Template = db.mock_model(model_name="Template",
            db_table="main_template", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)

=======
        
        Template = db.mock_model(model_name="Template",
            db_table="main_template", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db.create_table("main_systemtemplate", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), max_length=64, unique=True)),
            ("description", models.TextField(_("Description"), null=True, blank=True)),
            ("template", models.ForeignKey(Template, verbose_name=_("Template"))),
        ))
<<<<<<< HEAD

        db.send_create_signal("main", ["Template", "SystemTemplate"])

=======
        
        db.send_create_signal("main", ["Template", "SystemTemplate"])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_table("main_systemtemplate")
        db.delete_table("main_template")
