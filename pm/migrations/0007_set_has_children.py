# -*- coding: utf-8 -*-

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
# NOC modules
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        db = get_db()
        metrics = db.noc.ts.metrics
        has_children = {}
        for m in metrics.find({}).sort("name", 1):
            has_children[m["name"]] = False
            if "." in m["name"]:
                parent = ".".join(m["name"].split(".")[:-1])
                has_children[parent] = True
        if has_children:
            bulk = []
            for name in has_children:
                bulk += [UpdateOne({"name": name}, {
                    "$set": {
                        "has_children": has_children[name]
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
