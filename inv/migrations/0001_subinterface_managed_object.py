# ---------------------------------------------------------------------
# Initialize SubInterface.managed_object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # interface oid -> managed object id
        imo = {
            r["_id"]: r["managed_object"]
            for r in db.noc.interfaces.find({}, {"id": 1, "managed_object": 1})
        }
        # Update subinterface managed object id
        c = db.noc.subinterfaces
        for i_oid in imo:
            c.update_many({"interface": i_oid}, {"$set": {"managed_object": imo[i_oid]}})
