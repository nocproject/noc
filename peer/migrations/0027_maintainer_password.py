# ----------------------------------------------------------------------
# maintainer password
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
            "peer_maintainer",
            "password",
            models.CharField("Password", max_length=64, null=True, blank=True),
        )
        self.db.delete_column("peer_maintainer", "auth")
