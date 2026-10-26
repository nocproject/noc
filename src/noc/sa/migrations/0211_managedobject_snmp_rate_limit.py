# ----------------------------------------------------------------------
# ManagedObject.snmp_rate_limit
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        self.db.add_column(
            "sa_managedobjectprofile",
            "snmp_rate_limit",
            models.IntegerField(default=0),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_rate_limit",
            models.IntegerField(default=0),
        )
