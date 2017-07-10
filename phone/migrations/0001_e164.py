# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        db = get_db()
        coll = db["noc.dialplans"]
        if not coll.count():
            coll.insert({
                "name": "E.164",
                "description": "E.164 numbering plan",
                "mask": "\d{3,15}"
            })

    def backwards(self):
        pass
