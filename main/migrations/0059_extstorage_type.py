# ----------------------------------------------------------------------
# ExtStorage.type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        coll = db["extstorages"]
        coll.update_many({"enable_config_mirror": True}, {"$set": {"type": "config_mirror"}})
        coll.update_many({"enable_beef": True}, {"$set": {"type": "beef"}})
