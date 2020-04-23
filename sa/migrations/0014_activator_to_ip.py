# ----------------------------------------------------------------------
# activator to ip
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
            "sa_activator",
            "to_ip",
            models.GenericIPAddressField("To IP", null=True, blank=True, protocol="IPv4"),
        )
        self.db.execute("UPDATE sa_activator SET to_ip=ip")
        self.db.execute("ALTER TABLE sa_activator ALTER to_ip SET NOT NULL")
