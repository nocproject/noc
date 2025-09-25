# ----------------------------------------------------------------------
# activator
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
        # Model 'Activator'
        self.db.create_table(
            "sa_activator",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("ip", models.GenericIPAddressField("IP", protocol="IPv4")),
                ("auth", models.CharField("Auth String", max_length=64)),
                ("is_active", models.BooleanField("Is Active", default=True)),
            ),
        )
