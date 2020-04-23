# ----------------------------------------------------------------------
# dnszonerecord priority ttl
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
            "dns_dnszonerecord", "priority", models.IntegerField("Priority", null=True, blank=True)
        )
        self.db.add_column(
            "dns_dnszonerecord", "ttl", models.IntegerField("TTL", null=True, blank=True)
        )
