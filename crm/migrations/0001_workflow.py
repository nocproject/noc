# ----------------------------------------------------------------------
# Set workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import bson

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("wf", "0001_default_wf")]

    def migrate(self):
        db = self.mongo_db
        wf = bson.ObjectId("5a1d078e1bb627000151a17d")
        state = bson.ObjectId("5a1d07b41bb627000151a18b")
        db["noc.supplierprofiles"].update_many({}, {"$set": {"workflow": wf}})
        db["noc.subscriberprofiles"].update_many({}, {"$set": {"workflow": wf}})
        db["noc.subscribers"].update_many({}, {"$set": {"state": state}})
        db["noc.suppliers"].update_many({}, {"$set": {"state": state}})
