# -*- coding: utf-8 -*-
<<<<<<< HEAD

# Third-party modules
from bson.binary import Binary
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
# NOC modules
from noc.lib.nosql import get_db
=======
from noc.lib.nosql import get_db
from bson.binary import Binary
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Migration:
    def forwards(self):
        phash = {}
        db = get_db()
        metrics = db.noc.ts.metrics
<<<<<<< HEAD
        bulk = []
=======
        bulk = metrics.initialize_unordered_bulk_op()
        n = 0
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        for m in metrics.find({}).sort("name", 1):
            phash[m["name"]] = m["hash"]
            if "." in m["name"]:
                pn = ".".join(m["name"].split(".")[:-1])
                parent = phash[pn]
            else:
                parent = Binary("\x00" * 8)
<<<<<<< HEAD
            bulk += [UpdateOne({"_id": m["_id"]}, {
=======
            bulk.find({"_id": m["_id"]}).update({
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                "$set": {
                    "local": m["name"].split(".")[-1],
                    "parent": parent
                }
<<<<<<< HEAD
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
=======
            })
            n += 1
        if n:
            bulk.execute()

    def backwards(self):
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
