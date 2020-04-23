# ----------------------------------------------------------------------
# dnszoneprofile description
# ----------------------------------------------------------------------
# Copyright (C) 2009-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "dns_dnszoneprofile",
            "description",
            models.TextField("Description", blank=True, null=True),
        )
