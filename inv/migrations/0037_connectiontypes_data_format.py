# ----------------------------------------------------------------------
# Migrate ConnectionType.data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    MAX_BULK_SIZE = 500

    def migrate(self):
        coll = self.mongo_db["noc.connectiontypes"]
        bulk = []

        for doc in coll.find({}):
            data = doc.get("data")
            if isinstance(data, dict):
                new_data = []
                for md in data.items():
                    for attr, value in md[1].items():
                        new_data += [{"interface": md[0], "attr": attr, "value": value}]

                bulk += [UpdateOne({"_id": doc["_id"]}, {"$set": {"data": new_data}})]
                if len(bulk) >= self.MAX_BULK_SIZE:
                    coll.bulk_write(bulk)
                    bulk = []

        # Write rest of data
        if bulk:
            coll.bulk_write(bulk)
