# ----------------------------------------------------------------------
# profile theme
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
        self.db.add_column(
            "main_userprofile",
            "theme",
            models.CharField("Theme", max_length=32, null=True, blank=True),
        )
