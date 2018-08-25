# -*- coding: utf-8 -*-

# Third-party modules
from bson.binary import Binary
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
# NOC modules
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        phash = {}
        db = get_db()
        metrics = db.noc.ts.metrics
        bulk = []
        for m in metrics.find({}).sort("name", 1):
            phash[m["name"]] = m["hash"]
            if "." in m["name"]:
                pn = ".".join(m["name"].split(".")[:-1])
                parent = phash[pn]
            else:
                parent = Binary("\x00" * 8)
            bulk += [UpdateOne({"_id": m["_id"]}, {
                "$set": {
                    "local": m["name"].split(".")[-1],
                    "parent": parent
                }
            })]
        if bulk:
            print("Commiting changes to database")
            try:
                metrics.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print("Bulk write error: '%s'", e.details)
                print("Stopping check")

    def backwards(self):
        pass
