# ----------------------------------------------------------------------
# Address.name field
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
            "ip_address", "name", models.CharField("Name", max_length=255, null=True, blank=True)
        )
        self.db.execute("UPDATE ip_address SET name = fqdn")
        self.db.execute("ALTER TABLE ip_address ALTER name SET NOT NULL")
        self.db.execute("ALTER TABLE ip_address ALTER fqdn DROP NOT NULL")
