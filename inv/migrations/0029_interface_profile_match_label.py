# ----------------------------------------------------------------------
# Add InterfaceProfile match label to interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("inv", "0021_labels")]

    def migrate(self):
        bulk = []
        for ip in self.mongo_db["noc.interface_profiles"].find({}, {"_id": 1, "name": 1}):
            bulk += [
                UpdateMany(
                    {"profile": ip["_id"]},
                    {"$addToSet": {"effective_labels": f"noc::interface_profile::{ip['name']}::="}},
                )
            ]
        if bulk:
            self.mongo_db["noc.interfaces"].bulk_write(bulk)
