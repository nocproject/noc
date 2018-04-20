# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
# NOC modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        db = get_db()
        for c in (db.noc.alarmclasses, db.noc.eventclasses):
<<<<<<< HEAD
            bulk = []
            for d in c.find({}):
                text = d["text"]["en"]
                bulk += [UpdateOne({"_id": d["_id"]}, {
=======
            bulk = c.initialize_unordered_bulk_op()
            n = 0
            for d in c.find({}):
                text = d["text"]["en"]
                bulk.find({"_id": d["_id"]}).update({
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                })]
            if bulk:
                print("Commiting changes to database")
                try:
                    db.noc.fm.uptimes.bulk_write(bulk)
                    print("Database has been synced")
                except BulkWriteError as e:
                    print("Bulk write error: '%s'", e.details)
                    print("Stopping check")
=======
                })
                n += 1
            if n:
                bulk.execute()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def backwards(self):
        pass
