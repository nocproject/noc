from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        uc = get_db()["noc.cache.objectpaths"]
        dc = get_db()["noc.objectdata"]
        bulk = dc.initialize_unordered_bulk_op()
        n = 0
        for d in uc:
            bulk.find({
                "_id": d["_id"]
            }).upsert().update({
                "$set": {
                    "adm_path": d.get("adm_path", []),
                    "segment_path": d.get("segment_path", []),
                    "container_path": d.get("container_path", [])
                }
            })
            n += 1
        if n:
            bulk.execute()

    def backwards(self):
        pass
