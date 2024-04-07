# ---------------------------------------------------------------------
# Run calculate cfgTarget datastream
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        scheduler = self.mongo_db["noc.schedules.scheduler"]
        ts = datetime.datetime.now() + datetime.timedelta(minutes=20)
        scheduler.insert_one(
            {
                # "_id": ObjectId("6611715d0ece48259377c39c"),
                "s": "W",
                "runs": 0,
                "f": 0,
                "o": 0,
                "shard": None,
                "key": "noc.fixes.fix_rebuild_datastream.fix",
                "jcls": "noc.core.scheduler.calljob.CallJob",
                "ts": ts,
            }
        )
