# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobjectprofile cpe_profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        ManagedObjectProfile = self.db.mock_model(
            model_name="ManagedObjectProfile",
            db_table="sa_managedobjectprofile",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        AuthProfile = self.db.mock_model(
            model_name="AuthProfile",
            db_table="sa_authprofile",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.add_column(
            "sa_managedobjectprofile", "cpe_profile",
            models.ForeignKey(ManagedObjectProfile, verbose_name="Object Profile", blank=True, null=True)
        )
        self.db.add_column(
            "sa_managedobjectprofile", "cpe_auth_profile",
            models.ForeignKey(AuthProfile, verbose_name="Object Profile", blank=True, null=True)
        )
