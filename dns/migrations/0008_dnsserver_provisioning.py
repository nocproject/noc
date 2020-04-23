# ----------------------------------------------------------------------
# dnsserver provisioning
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
            "dns_dnsserver",
            "provisioning",
            models.CharField("Provisioning", max_length=128, blank=True, null=True),
        )
        self.db.execute(
            "UPDATE dns_dnsserver SET provisioning=%s", ["%(rsync)s -av --delete * /tmp/dns"]
        )
