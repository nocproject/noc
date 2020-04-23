# ----------------------------------------------------------------------
# no category
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_table("kb_kbentrytemplate_categories")
        self.db.delete_table("kb_kbentry_categories")
        self.db.delete_table("kb_kbcategory")
