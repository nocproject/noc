# ----------------------------------------------------------------------
# Cleanup bad object_status documents
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.mongo_db["noc.cache.object_status"].delete_many({"object": {"$exists": False}})
