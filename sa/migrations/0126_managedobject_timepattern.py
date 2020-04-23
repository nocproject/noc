# ----------------------------------------------------------------------
# managedobject time_pattern
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
        TimePattern = self.db.mock_model(model_name="TimePattern", db_table="main_timepattern")
        self.db.add_column(
            "sa_managedobject",
            "time_pattern",
            models.ForeignKey(TimePattern, null=True, blank=True, on_delete=models.CASCADE),
        )
