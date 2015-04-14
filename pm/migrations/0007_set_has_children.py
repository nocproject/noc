# -*- coding: utf-8 -*-
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
            bulk = metrics.initialize_unordered_bulk_op()
            for name in has_children:
                bulk.find({"name": name}).update({
                    "$set": {
                        "has_children": has_children[name]
                    }
                })
            bulk.execute()

    def backwards(self):
        pass