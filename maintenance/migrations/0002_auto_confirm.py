# ----------------------------------------------------------------------
# Auto confirm
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        now = datetime.datetime.now()
        db.noc.maintenance.update_many(
            {"is_completed": False, "auto_confirm": {"$exists": False}, "stop": {"$lte": now}},
            {"$set": {"is_completed": True}},
        )

        db.noc.maintenance.update_many(
            {"is_completed": False, "auto_confirm": {"$exists": False}, "stop": {"$gte": now}},
            {"$set": {"auto_confirm": True}},
        )
