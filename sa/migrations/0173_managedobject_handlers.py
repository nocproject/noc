# ----------------------------------------------------------------------
# managedobject handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        handlers = set()
        proccessed = set()
        for (h,) in self.db.execute("SELECT DISTINCT config_filter_handler FROM sa_managedobject"):
            if h:
                handlers.add(h)
        for (h,) in self.db.execute(
            "SELECT DISTINCT config_diff_filter_handler FROM sa_managedobject"
        ):
            if h:
                handlers.add(h)
        if handlers:
            coll = self.mongo_db["handlers"]
            for h in handlers:
                name = h.split(".")[-2]
                proccessed.add(h)
                coll.insert_one({"_id": h, "name": name, "allow_config_filter": True})
        handlers = set()
        for (h,) in self.db.execute(
            "SELECT DISTINCT config_validation_handler FROM sa_managedobject"
        ):
            if h:
                handlers.add(h)
        if handlers:
            coll = self.mongo_db["handlers"]
            for h in handlers:
                name = h.split(".")[-2]
                if h in proccessed:
                    coll.update_one({"_id": h}, {"$set": {"allow_config_validation": True}})
                    continue
                coll.insert_one({"_id": h, "name": name, "allow_config_validation": True})
