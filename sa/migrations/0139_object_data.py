from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        uc = get_db()["noc.objectuplinks"]
        dc = get_db()["noc.objectdata"]
        bulk = dc.initialize_unordered_bulk_op()
        n = 0
        for d in uc.find():
            bulk.insert({
                "_id": d["_id"],
                "uplinks": d.get("uplinks", [])
            })
            n += 1
        if n:
            bulk.execute()

    def backwards(self):
        pass
