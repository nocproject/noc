# ----------------------------------------------------------------------
# Add column SlowOp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------



# NOC modules
from noc.core.migration.base import BaseMigration

class Migration(BaseMigration):

    def migrate(self):
        collection = self.mongo_db.noc.slowop
        collection.update_many({}, {"$set": {"params": {}}})