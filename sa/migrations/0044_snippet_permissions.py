# ----------------------------------------------------------------------
# snippet permissions
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
            "sa_commandsnippet",
            "permission_name",
            models.CharField("Permission Name", max_length=64, null=True, blank=True),
        )
        self.db.add_column(
            "sa_commandsnippet",
            "display_in_menu",
            models.BooleanField("Show in menu", default=False),
        )
