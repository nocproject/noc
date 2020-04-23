# ----------------------------------------------------------------------
# eventtrigger handler
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
            "fm_eventtrigger",
            "handler",
            models.CharField("Handler", max_length=128, null=True, blank=True),
        )
