# ----------------------------------------------------------------------
# dnszonerecord change fields
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
        self.db.rename_column("dns_dnszonerecord", "left", "name")
        self.db.rename_column("dns_dnszonerecord", "right", "content")
        self.db.execute(
            """
            ALTER TABLE dns_dnszonerecord
            ALTER COLUMN content TYPE VARCHAR(256)
            """
        )
        self.db.add_column(
            "dns_dnszonerecord", "type", models.CharField("Type", max_length=16, default="")
        )
