# ----------------------------------------------------------------------
# snmp community
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
            "sa_managedobject",
            "snmp_ro",
            models.CharField("RO Community", blank=True, null=True, max_length=64),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_rw",
            models.CharField("RW Community", blank=True, null=True, max_length=64),
        )
