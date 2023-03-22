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
    WF_MANAGED = "641b35e6fa01fd032a1f61f1"
    WF_UNMANAGED = "641b371eb846e3cc661ea8b5"

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
            self.db.execute(
                "UPDATE sa_managedobject SET state=%s WHERE is_managed=True", [self.WF_MANAGED]
            )
            self.db.execute(
                "UPDATE sa_managedobject SET state=%s WHERE is_managed=False", [self.WF_UNMANAGED]
            )
