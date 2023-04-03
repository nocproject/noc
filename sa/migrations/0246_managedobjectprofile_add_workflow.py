# ---------------------------------------------------------------------
# Add Workflow to ManagedObjectProfile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.model.fields import DocumentReferenceField

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("wf", "0007_managedobject_default")]
    WF_DEFAULT = "641b35e6fa01fd032a1f61ef"

    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "workflow",
            DocumentReferenceField("wf.Workflow", null=True, blank=True),
        )
        self.db.execute("UPDATE sa_managedobjectprofile SET workflow=%s", [self.WF_DEFAULT])
