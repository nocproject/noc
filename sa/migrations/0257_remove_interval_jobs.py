# ---------------------------------------------------------------------
# Remove interval jobs
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        mdb = self.mongo_db
        for d in mdb.noc.pools.find():
            mdb[f"noc.schedules.discovery.{d['name']}"].delete_many(
                {"jcls": "noc.services.discovery.jobs.interval.job.IntervalDiscoveryJob"},
            )
