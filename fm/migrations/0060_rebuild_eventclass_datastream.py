# ----------------------------------------------------------------------
# Rebuild EventClass Datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.mongo_db["noc.schedules.scheduler"].insert_one(
            {
                "ts": datetime.datetime.now().replace(microsecond=0),
                "s": "R",
                "runs": 0,
                "f": 0,
                "o": 0,
                "shard": 0,
                "mruns": 1,
                "jcls": "noc.core.scheduler.calljob.CallJob",
                "key": "noc.main.handlers.rebuild_datastream.generate_changes",
                "data": {"model_id": "fm.EventClass"},
            }
        )
        self.mongo_db["noc.schedules.scheduler"].insert_one(
            {
                "ts": datetime.datetime.now().replace(microsecond=0),
                "s": "R",
                "runs": 0,
                "f": 0,
                "o": 0,
                "shard": 0,
                "mruns": 1,
                "jcls": "noc.core.scheduler.calljob.CallJob",
                "key": "noc.main.handlers.rebuild_datastream.generate_changes",
                "data": {"model_id": "fm.DispositionRule"},
            }
        )
