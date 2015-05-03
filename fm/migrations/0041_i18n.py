# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        db = get_db()
        for c in (db.noc.alarmclasses, db.noc.eventclasses):
            bulk = c.initialize_unordered_bulk_op()
            n = 0
            for d in c.find({}):
                text = d["text"]["en"]
                bulk.find({"_id": d["_id"]}).update({
                    "$set": {
                        "subject_template": text["subject_template"],
                        "body_template": text["body_template"],
                        "symptoms": text["symptoms"],
                        "probable_causes": text["probable_causes"],
                        "recommended_actions": text["recommended_actions"]
                    },
                    "$unset": {
                        "text": ""
                    }
                })
                n += 1
            if n:
                bulk.execute()

    def backwards(self):
        pass
