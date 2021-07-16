# ----------------------------------------------------------------------
# Migrate SLAProbe to workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Third-party modules
from pymongo import UpdateMany
from bson import ObjectId

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("wf", "0005_slaprobe_default")]

    def migrate(self):
        coll = self.mongo_db["noc.sla_probes"]
        coll.bulk_write(
            [
                # "Planned"
                UpdateMany({}, {"$set": {"state": ObjectId("607a7e1d3d18d4fb3c12032a")}}),
            ]
        )
        # Service Profile Workflow
        self.mongo_db["noc.sla_profiles"].bulk_write(
            [UpdateMany({}, {"$set": {"workflow": ObjectId("607a7dddff3a857a47600b9b")}})]
        )
