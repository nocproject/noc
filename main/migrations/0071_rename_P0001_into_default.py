# ----------------------------------------------------------------------
# Rename P0001 into default
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db_m = self.mongo_db
        collection = db_m.noc.pools
        cn_pools = collection.count_documents({})
        id_mongo = None
        if cn_pools == 1:
            id_mongo = collection.find({"name": "P0001"})._id

        rows = self.db.execute("select name from sa_managedobject")
        fl_pqr = False
        if len(rows) == 0 or (len(rows) == 1 and rows[0] == "SAE"):
            fl_pqr = True

        if id_mongo and fl_pqr:
            collection.update_one({"_id": id_mongo}, {"$set": {"name": "default"}})
