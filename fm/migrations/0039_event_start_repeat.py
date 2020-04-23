# ----------------------------------------------------------------------
# event start repeat
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        for c in [db.noc.events.active, db.noc.events.archive]:
            # @todo: Set start_timestamp = timestamp
            c.update_many({"repeats": {"$exists": False}}, {"$set": {"repeats": 1}})
