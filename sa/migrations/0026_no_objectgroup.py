# ---------------------------------------------------------------------
# no object group
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("cm", "0016_no_objectgroup")]

    def migrate(self):
        self.db.delete_table("sa_managedobject_groups")
        self.db.delete_table("sa_managedobjectselector_filter_groups")
        self.db.delete_table("sa_objectgroup")
