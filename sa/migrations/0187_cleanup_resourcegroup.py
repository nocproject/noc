# ----------------------------------------------------------------------
# Remove _legacy_id from resource group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("phone", "0002_migrate_termination_groups")]

    def migrate(self):
        db = self.mongo_db
        coll = db["resourcegroups"]
        coll.update_many({"_legacy_id": {"$exists": True}}, {"$unset": {"_legacy_id": ""}})
