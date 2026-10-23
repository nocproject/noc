# ----------------------------------------------------------------------
# Initialize bi_id field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne
import bson

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash

PG_CHUNK = 500
MONGO_CHUNK = 500


class Migration(BaseMigration):
    def migrate(self) -> None:
        MODELS = [
            "sa_administrativedomain",
            "sa_authprofile",
            "sa_managedobject",
            "sa_managedobjectprofile",
            "sa_terminationgroup",
        ]
        # Update postgresql tables
        for table in MODELS:
            rows = self.db.execute(f"SELECT id FROM {table} WHERE bi_id IS NULL")
            values = [f"({int(r[0])}, {int(bi_hash(r[0]))})" for r in rows]
            while values:
                chunk, values = values[:PG_CHUNK], values[PG_CHUNK:]
                self.db.execute(
                    """
                    UPDATE {} AS t
                    SET
                      bi_id = c.bi_id
                    FROM (
                      VALUES
                      {}
                    ) AS c(id, bi_id)
                    WHERE c.id = t.id
                    """.format(table, ",\n".join(chunk))
                )
        # Update mongodb collections
        mdb = self.mongo_db
        for coll_name in ["noc.profiles", "noc.services", "noc.serviceprofiles"]:
            coll = mdb[coll_name]
            updates = []
            for d in coll.find({"bi_id": {"$exists": False}}, {"_id": 1}):
                updates.append(
                    UpdateOne({"_id": d["_id"]}, {"$set": {"bi_id": bson.Int64(bi_hash(d["_id"]))}})
                )
                if len(updates) >= MONGO_CHUNK:
                    coll.bulk_write(updates)
                    updates = []
            if updates:
                coll.bulk_write(updates)
        # Alter bi_id fields and create indexes
        for table in MODELS:
            self.db.execute(f"ALTER TABLE {table} ALTER bi_id SET NOT NULL")
            self.db.create_index(table, ["bi_id"], unique=True)
