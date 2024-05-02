# ----------------------------------------------------------------------
# ManagedObjectProfile enable box discovery_param_data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_periodic_discovery_snmp_check",
            models.BooleanField(default=False),
        )
