# ----------------------------------------------------------------------
# managedobject l2domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobject", "l2domain", DocumentReferenceField("self", null=True, blank=True)
        )
        self.db.create_index("sa_managedobject", ["l2domain"], unique=False)
