# ----------------------------------------------------------------------
# ManagedObjectProfile.enable_interface_autocreation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_interface_autocreation",
            models.BooleanField(default=False),
        )
