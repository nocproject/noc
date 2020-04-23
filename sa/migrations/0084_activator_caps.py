# ----------------------------------------------------------------------
# activator caps
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
            "sa_activator", "min_sessions", models.IntegerField("Min Sessions", default=0)
        )
        self.db.add_column(
            "sa_activator", "min_members", models.IntegerField("Min Members", default=0)
        )
