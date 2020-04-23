# ----------------------------------------------------------------------
# managedobjectprofile ipam sync
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
            "sa_managedobjectprofile", "sync_ipam", models.BooleanField("Sync. IPAM", default=False)
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "fqdn_template",
            models.TextField("FQDN template", null=True, blank=True),
        )
