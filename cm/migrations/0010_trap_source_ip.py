# ----------------------------------------------------------------------
# trap source ip
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
            "cm_config",
            "trap_source_ip",
            models.GenericIPAddressField("Trap Source IP", blank=True, null=True, protocol="IPv4"),
        )
        self.db.add_column(
            "cm_config",
            "trap_community",
            models.CharField("Trap Community", blank=True, null=True, max_length=64),
        )
