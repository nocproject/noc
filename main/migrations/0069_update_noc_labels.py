# ----------------------------------------------------------------------
# Migrate add uuid fild
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
import uuid

class Migration(BaseMigration):

    def migrate(self):
        coll =  self.mongo_db["labels"]
        for p in coll.find({}):
             u = uuid.uuid4()
             self.mongo_db["labels"].update_one({"name": p['name']}, {"$set": {"uuid": u}})

