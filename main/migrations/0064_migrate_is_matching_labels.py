# ----------------------------------------------------------------------
# Migrate is_regex to is_matching field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0063_migrate_filter_labels")]

    def migrate(self):
        self.mongo_db["labels"].update_many({"is_regex": True}, {"$set": {"is_matching": True}})
