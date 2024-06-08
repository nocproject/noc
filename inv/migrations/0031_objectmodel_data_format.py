# ----------------------------------------------------------------------
# Migrate Object.data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    MAX_BULK_SIZE = 500

    def migrate(self):
        coll = self.mongo_db["noc.objectmodels"]
        bulk = []
        for doc in coll.find({}, no_cursor_timeout=True):
            data = doc.get("data") or {}
            # if mongo data is {} - unsupported operand type(s) for +=: 'BaseDict' and 'list'
            if isinstance(data, list):
                continue  # No data or already converted
            new_data = []
            for mi in data:
                for attr, value in data[mi].items():
                    new_data += [{"interface": mi, "attr": attr, "value": value}]
            bulk += [UpdateOne({"_id": doc["_id"]}, {"$set": {"data": new_data}})]
            if len(bulk) >= self.MAX_BULK_SIZE:
                coll.bulk_write(bulk)
                bulk = []
        # Write rest of data
        if bulk:
            coll.bulk_write(bulk)
