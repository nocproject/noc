# ----------------------------------------------------------------------
# Create interval task
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import random
import datetime

# Third-party modules
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.scheduler.job import Job

INTERVAL_DISCOVERY_JOB = "noc.services.discovery.jobs.interval.job.IntervalDiscoveryJob"
CHINK = 500


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        lc = [n for n in db.list_collection_names() if n.startswith("noc.schedules.discovery.")]
        now = datetime.datetime.now()
        for discovery in lc:
            coll = db[discovery]
            _, pool = discovery.rsplit(".", 1)
            bulk = []
            for row in coll.find(
                {"jcls": "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"}
            ):
                bulk += [
                    InsertOne(
                        {
                            Job.ATTR_CLASS: INTERVAL_DISCOVERY_JOB,
                            Job.ATTR_KEY: row["key"],
                            Job.ATTR_STATUS: Job.S_WAIT,
                            Job.ATTR_RUNS: 0,
                            Job.ATTR_FAULTS: 0,
                            Job.ATTR_OFFSET: random.random(),
                            Job.ATTR_TS: row.get(Job.ATTR_TS, now),
                        }
                    )
                ]
                if len(bulk) >= CHINK:
                    coll.bulk_write(bulk)
                    bulk = []
            if bulk:
                coll.bulk_write(bulk)
