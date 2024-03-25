# ----------------------------------------------------------------------
# managedobject set pool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        mdb = self.mongo_db
        for d in mdb.noc.pools.find():
            pid = 1 if d["name"] == "default" else int(d["name"][1:])
            self.db.execute(
                "UPDATE sa_managedobject SET pool=%s WHERE activator_id=%s", [str(d["_id"]), pid]
            )
        # Adjust scheme values
        # For smooth develop -> post-microservice migration
        self.db.execute("UPDATE sa_managedobject SET scheme = scheme + 1")
