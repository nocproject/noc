# ----------------------------------------------------------------------
# ManagedObjectProfile.enable_interface_autocreation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from django.db import models


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_interface_autocreation",
            models.BooleanField(default=False),
        )
