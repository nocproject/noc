from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        # Get profile record mappings
        pcoll = get_db()["noc.profiles"]
        pcrcoll = get_db()["noc.profilecheckrules"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = d["_id"]
        # Update
        for p in pmap:
            pcrcoll.update({
                "profile": p
            }, {
                "$set": {
                    "profile": pmap[p]
                }
            }, multi=True)

    def backwards(self):
        pass
