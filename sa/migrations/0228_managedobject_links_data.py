# ----------------------------------------------------------------------
# Migrate ManagedObject Links Data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import connection
from psycopg2.extras import execute_values
from itertools import chain

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.links"]
        links = []
        for data in coll.aggregate(
            [
                {"$project": {"neighbors": "$linked_objects", "linked_objects": 1}},
                {"$unwind": "$linked_objects"},
                {"$group": {"_id": "$linked_objects", "neighbors": {"$push": "$neighbors"}}},
            ]
        ):
            nei = set(chain(*data["neighbors"]))
            nei.remove(data["_id"])
            if not nei:
                continue
            links.append((data["_id"], list(nei)))
        cursor = connection.cursor()
        execute_values(
            cursor,
            """
                UPDATE sa_managedobject AS mo
                SET links = c.links
                FROM (VALUES %s) AS c(moid, links)
                WHERE c.moid = mo.id
            """,
            links,
            page_size=1000,
        )
