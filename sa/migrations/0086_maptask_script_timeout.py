# ----------------------------------------------------------------------
# maptask script_timeout
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
            "sa_maptask",
            "script_timeout",
            models.IntegerField("Script timeout", null=True, blank=True),
        )
