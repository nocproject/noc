# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.create_table("sa_authprofile", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True,
                auto_created=True)),
            ("name", models.CharField("Name", max_length=64, unique=True)),
            ("description", models.TextField("Description", null=True, blank=True)),
            ("type", models.CharField("Name", max_length=1)),
            ("user", models.CharField("User", max_length=32, blank=True, null=True)),
            ("password",  models.CharField("Password", max_length=32, blank=True, null=True)),
            ("super_password", models.CharField("Super Password", max_length=32, blank=True, null=True)),
            ("snmp_ro", models.CharField("RO Community", blank=True, null=True, max_length=64)),
            ("snmp_rw", models.CharField("RW Community", blank=True, null=True, max_length=64))
        ))
        # Mock Models
        AuthProfile = db.mock_model(
            model_name="AuthProfile",
            db_table="sa_authprofile", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)

        db.add_column("sa_managedobject", "auth_profile",
                      models.ForeignKey(AuthProfile, verbose_name="Auth Profile", null=True, blank=True))

    def backwards(self):
        db.drop_column("sa_managedobject", "auth_profile_id")
        db.delete_table("sa_authprofile")
