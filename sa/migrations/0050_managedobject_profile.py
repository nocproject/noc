# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        ManagedObjectProfile = db.mock_model(model_name="ManagedObjectProfile", db_table="sa_managedobjectprofile",
            db_tablespace="", pk_field_name="id", pk_field_type=models.AutoField)

        db.add_column("sa_managedobject", "object_profile",
            models.ForeignKey(ManagedObjectProfile, null=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "object_profile_id")
