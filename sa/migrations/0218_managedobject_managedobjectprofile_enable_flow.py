# ----------------------------------------------------------------------
# ManagedObject and ManagedObjectProfile enable netflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):

        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_flow",
            models.BooleanField(default=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "enable_flow",
            models.BooleanField(default=True),
        )
