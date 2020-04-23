# ----------------------------------------------------------------------
# managedobjectselector finish tags migration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Drop old tags
        self.db.delete_column("sa_managedobjectselector", "filter_tags")
        # Rename new tags
        self.db.rename_column("sa_managedobjectselector", "tmp_filter_tags", "filter_tags")
