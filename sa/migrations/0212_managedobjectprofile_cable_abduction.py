# ----------------------------------------------------------------------
# ManagedObjectProfile cable abduction settings
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
            "abduct_detection_window",
            models.IntegerField(default=0),
        )
        self.db.add_column(
            "sa_managedobjectprofile", "abduct_detection_threshold", models.IntegerField(default=0)
        )
