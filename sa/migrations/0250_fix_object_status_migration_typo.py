# ----------------------------------------------------------------------
# Cleanup bad object_status documents
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.cache.object_status"]
        coll.update_many({"statue": {"$exists": True}}, {"$set": {"status": True}})
        coll.update_many({"statue": {"$exists": True}}, {"$unset": {"statue": 1}})
