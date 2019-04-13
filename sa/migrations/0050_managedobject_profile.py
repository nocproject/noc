# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from django.db import models
from south.db import db


class Migration(object):
    def forwards(self):
        ManagedObjectProfile = db.mock_model(
            model_name="ManagedObjectProfile",
            db_table="sa_managedobjectprofile",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        db.add_column("sa_managedobject", "object_profile", models.ForeignKey(ManagedObjectProfile, null=True))

    def backwards(self):
        db.delete_column("sa_managedobject", "object_profile_id")
