# ---------------------------------------------------------------------
# Set ThresholdProfiles uuid
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import uuid

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        thps = self.mongo_db["thresholdprofiles"]
        for thp in thps.find({"uuid": {"$exists": False}}):
            u = uuid.uuid4()
            thps.update_one({"_id": thp["_id"]}, {"$set": {"uuid": u}})
