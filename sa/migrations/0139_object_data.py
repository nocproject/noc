# -*- coding: utf-8 -*-

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import InsertOne
# NOC modules
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        uc = get_db()["noc.objectuplinks"]
        dc = get_db()["noc.objectdata"]
        bulk = []
        for d in uc.find():
            bulk += [InsertOne({
                "_id": d["_id"],
                "uplinks": d.get("uplinks", [])
            })]
        if bulk:
            print("Commiting changes to database")
            try:
                dc.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print("Bulk write error: '%s'", e.details)
                print("Stopping check")

    def backwards(self):
        pass
