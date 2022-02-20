# ----------------------------------------------------------------------
# Migrate ManagedObject Links Data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from itertools import chain

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.links"]
        for data in coll.aggregate(
            [
                {"$project": {"neighbors": "$linked_objects", "linked_objects": 1}},
                {"$unwind": "$linked_objects"},
                {"$group": {"_id": "$linked_objects", "neighbors": {"$push": "$neighbors"}}},
            ]
        ):
            links = set(chain(*data["neighbors"]))
            links.remove(data["_id"])
            if not links:
                continue
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET links = %s
                WHERE id = %s
                """,
                [
                    list(links),
                    data["_id"],
                ],
            )
