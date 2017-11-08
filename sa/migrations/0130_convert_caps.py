# -*- coding: utf-8 -*-

from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        def convert(doc):
            def convert_caps(ci):
                return {
                    "capability": ci["capability"],
                    "value": ci["discovered_value"],
                    "source": sources.get(ci["capability"], "caps")
                }

            return {
                "_id": doc["object"],
                "caps": [convert_caps(c) for c in doc["caps"]]
            }

        db = get_db()
        caps = db["noc.sa.objectcapabilities"]
        if not caps.count():
            return
        caps.rename("noc.sa.objectcapabilities_old", dropTarget=True)
        old_caps = db["noc.sa.objectcapabilities_old"]
        new_caps = db["noc.sa.objectcapabilities"]
        sources = {}
        d = db["noc.inv.capabilities"].find_one({"name": "DB | Interfaces"})
        if d:
            sources[d["_id"]] = "interface"

        CHUNK = 500
        data = [convert(d) for d in old_caps.find({}) if d.get("object")]
        while data:
            chunk, data = data[:CHUNK], data[CHUNK:]
            new_caps.insert(chunk)
            # old_caps.drop()

    def backwards(self):
        pass
