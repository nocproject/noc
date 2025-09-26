# ----------------------------------------------------------------------
# authprofile suggest
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
        # Mock Models
        AuthProfile = self.db.mock_model(model_name="AuthProfile", db_table="sa_authprofile")
        self.db.create_table(
            "sa_authprofilesuggestsnmp",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("auth_profile", models.ForeignKey(AuthProfile, on_delete=models.CASCADE)),
                ("snmp_ro", models.CharField("RO Community", blank=True, null=True, max_length=64)),
                ("snmp_rw", models.CharField("RW Community", blank=True, null=True, max_length=64)),
            ),
        )
        self.db.create_table(
            "sa_authprofilesuggestcli",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("auth_profile", models.ForeignKey(AuthProfile, on_delete=models.CASCADE)),
                ("user", models.CharField("User", max_length=32, blank=True, null=True)),
                ("password", models.CharField("Password", max_length=32, blank=True, null=True)),
                (
                    "super_password",
                    models.CharField("Super Password", max_length=32, blank=True, null=True),
                ),
            ),
        )
