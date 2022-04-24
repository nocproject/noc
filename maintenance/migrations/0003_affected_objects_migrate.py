# ----------------------------------------------------------------------
# Remove unused legacy fields from User model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import bson

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        ao_coll = self.mongo_db["noc.affectedobjects"]
        db = self.mongo_db
        for ao in db.noc.maintenance.find({"affected_objects": {"$exists": True}}):
            affected_objects = ao["affected_objects"]
            db.noc.maintenance.update_one({"_id": ao["_id"]}, {"$unset": {"affected_objects": 1}})
            if not ao["is_completed"]:
                ao_id = bson.ObjectId()
                ao_data = {
                    "_id": ao_id,
                    "maintenance": ao["_id"],
                    "affected_objects": affected_objects,
                }
                ao_coll.insert_one(ao_data)
