# -*- coding: utf-8 -*-
from noc.lib.nosql import get_db
from bson.binary import Binary


class Migration:
    def forwards(self):
        phash = {}
        db = get_db()
        metrics = db.noc.ts.metrics
        bulk = metrics.initialize_unordered_bulk_op()
        n = 0
        for m in metrics.find({}).sort("name", 1):
            phash[m["name"]] = m["hash"]
            if "." in m["name"]:
                pn = ".".join(m["name"].split(".")[:-1])
                parent = phash[pn]
            else:
                parent = Binary("\x00" * 8)
            bulk.find({"_id": m["_id"]}).update({
                "$set": {
                    "local": m["name"].split(".")[-1],
                    "parent": parent
                }
            })
            n += 1
        if n:
            bulk.execute()

    def backwards(self):
        pass