# ----------------------------------------------------------------------
# Restore User.last_login
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import DateTimeField

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if not self.db.has_column("auth_user", "last_login"):
            self.db.add_column(
                "auth_user", "last_login", DateTimeField("Last Login", blank=True, null=True)
            )
