# ----------------------------------------------------------------------
# Migrate Prefix.state field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.fields import DocumentReferenceField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    WF_FREE = "5a17f61b1bb6270001bd0328"

    def migrate(self):
        # Create new ManagedObject.state
        self.db.add_column(
            "sa_managedobject", "state", DocumentReferenceField("wf.State", null=True, blank=True)
        )
        columns = {
            "state_changed": "State Changed",
            "expired": "Expired",
            "last_seen": "Last Seen",
            "first_discovered": "First Discovered",
        }
        for column, column_title in columns.items():
            self.db.add_column(
                "sa_managedobject",
                column,
                models.DateTimeField(column_title, blank=True, null=True),
            )
