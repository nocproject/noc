# -*- coding: utf-8 -*-
from south.db import db
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        collection = get_db()["noc.extnrittmap"]
        mappings = [
            (d["managed_object"], str(d["tt_system"]),
             str(d["queue"]), str(d["remote_id"]))
            for d in collection.find()
        ]
        for mo, tts, ttqueue, ttid in mappings:
            db.execute(
                """UPDATE sa_managedobject 
                SET tt_system = %s,
                    tt_queue = %s,
                    tt_system_id = %s 
                WHERE id = %s""",
                [tts, ttqueue, ttid, mo]
            )

    def backwards(self):
        pass
