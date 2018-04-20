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
from noc.core.model.fields import CIDRField

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
        db.create_table("main_prefixtable", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), max_length=128, unique=True)),
            ("description", models.TextField(_("Description"), null=True, blank=True)),
        ))
<<<<<<< HEAD

        PrefixTable = db.mock_model(model_name="PrefixTable",
            db_table="main_prefixtable", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)

=======
        
        PrefixTable = db.mock_model(model_name="PrefixTable",
            db_table="main_prefixtable", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db.create_table("main_prefixtableprefix", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("table", models.ForeignKey(PrefixTable, verbose_name = _("Prefix Table"))),
            ("afi", models.CharField(_("Address Family"),max_length=1,
                    choices=[("4", _("IPv4")), ("6", _("IPv6"))])),
            ("prefix", CIDRField(_("Prefix")))
        ))
<<<<<<< HEAD

        db.send_create_signal("main", ["PrefixTable", "PrefixTablePrefix"])

    def backwards(self):
        db.delete_table("main_prefixtable")
        db.delete_table("main_prefixtableprefix")

=======
        
        db.send_create_signal("main", ["PrefixTable", "PrefixTablePrefix"])
    
    def backwards(self):
        db.delete_table("main_prefixtable")
        db.delete_table("main_prefixtableprefix")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
