# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Create ResourceState
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from django.db import models
=======
##----------------------------------------------------------------------
## Create ResourceState
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC modules
from noc.main.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Migration:
    def forwards(self):
        # ResourceState
        ResourceState = db.mock_model(model_name="ResourceState",
            db_table="main_resourcestate", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db.create_table("main_resourcestate", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),            
            ("name", models.CharField("Name", max_length=32, unique=True)),
            ("description", models.TextField(null=True, blank=True)),
            ("is_active", models.BooleanField(default=True)),
            ("is_starting", models.BooleanField(default=True)),
            ("is_default", models.BooleanField(default=False)),
            ("is_provisioned", models.BooleanField(default=True)),
            ("step_to", models.ForeignKey(ResourceState, blank=True, null=True))
            )
        )
        db.send_create_signal("main", ["ResourceState"])

    def backwards(self):
        db.delete_table("main_resourcestate")
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
