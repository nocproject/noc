# ---------------------------------------------------------------------
# Create *default* pool
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0005_activator")]

    def migrate(self):
        mdb = self.mongo_db
        mdb.noc.pools.insert_one({"name": "default", "description": "default"})
        for a_id, name in self.db.execute("SELECT id, name FROM sa_activator"):
            mdb.noc.pools.insert_one({"name": "P%04d" % a_id, "description": name})

    def backwards(self):
        pass
