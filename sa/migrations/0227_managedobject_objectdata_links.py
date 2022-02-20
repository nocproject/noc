# ----------------------------------------------------------------------
# Migrate ManagedObject Links
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.contrib.postgres.fields import ArrayField
from django.db.models import IntegerField

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create links fields
        self.db.add_column(
            "sa_managedobject",
            "links",
            ArrayField(IntegerField(), db_index=True, null=True, blank=True, default=lambda: "{}"),
        )
