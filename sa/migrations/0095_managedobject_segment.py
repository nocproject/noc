# ----------------------------------------------------------------------
# managedobject segment
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    depends_on = [("inv", "0010_default_segment")]

    def migrate(self):
        self.db.add_column(
            "sa_managedobject", "segment", DocumentReferenceField("self", null=True, blank=True)
        )
        self.db.create_index("sa_managedobject", ["segment"], unique=False)
