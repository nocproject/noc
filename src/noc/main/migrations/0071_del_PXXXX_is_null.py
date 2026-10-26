# ----------------------------------------------------------------------
# Remove Pxxxx from sa_managedobject if quantity is zero.
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        coll = self.mongo_db["noc.pools"]
        pattern = re.compile(r"^P\d{4}$")

        for pool in coll.find({}):
            rows_obj = self.db.execute(
                "select name from sa_managedobject where pool = %s", [str(pool["_id"])]
            )
            if not rows_obj and pattern.match(pool["name"]):
                coll.delete_one({"_id": pool["_id"]})
