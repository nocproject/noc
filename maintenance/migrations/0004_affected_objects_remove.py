# ----------------------------------------------------------------------
# Remove AffectedObjects, Migrate to ManagedObjects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import orjson

# NOC modules
from noc.core.migration.base import BaseMigration

SQL_ADD = """
  UPDATE sa_managedobject
  SET affected_maintenances = jsonb_insert(affected_maintenances, %s, %s::jsonb)
  WHERE id = ANY(%s::int[])
  """


class Migration(BaseMigration):
    depends_on = [("sa", "0231_managedobject_affected_maintenances")]

    def migrate(self):
        db = self.mongo_db
        processed = {
            am
            for (am,) in self.db.execute(
                "SELECT jsonb_object_keys(affected_maintenances) FROM sa_managedobject"
            )
        }
        for ao in db.noc.affectedobjects.aggregate(
            [
                {"$match": {"maintenance": {"$exists": True}}},
                {
                    "$project": {"_id": 0, "maintenance": 1, "objects": "$affected_objects.object"},
                },
            ]
        ):
            m_id = ao["maintenance"]
            if not ao["objects"] or str(m_id) in processed:
                continue
            mai = db.noc.maintenance.find_one({"_id": m_id})
            if not mai:
                # Not Find Maintenance
                continue
            if mai["stop"] < datetime.datetime.now():
                continue
            # Insert to ManagedObject
            self.db.execute(
                SQL_ADD,
                [
                    f"{{{m_id}}}",
                    orjson.dumps({"start": mai["start"], "stop": mai["stop"]}).decode("utf-8"),
                    ao["objects"],
                ],
            )
        db.noc.affectedobjects.drop()
