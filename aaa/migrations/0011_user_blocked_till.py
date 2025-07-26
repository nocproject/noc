# ----------------------------------------------------------------------
# Restore User.blocked_till
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import DateTimeField

# NOC modules
from noc.core.migration.base import BaseMigration
from django.contrib.postgres.fields import ArrayField


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column("auth_user", "blocked_till", DateTimeField(blank=True, null=True))
        self.db.add_column(
            "auth_user", "failed_history", ArrayField(DateTimeField(), blank=True, null=True)
        )
