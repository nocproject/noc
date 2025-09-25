# ----------------------------------------------------------------------
# zonerecordtype validation
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
            "dns_dnszonerecordtype",
            "validation",
            models.CharField("Validation", max_length=256, blank=True, null=True),
        )
