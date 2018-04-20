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
from noc.lib.dateutils import total_seconds


class Migration:
    def forwards(self):
        db = get_db()
<<<<<<< HEAD
        bulk = []
        for d in db.noc.fm.uptimes.find({}):
            bulk += [UpdateOne({"_id": d["_id"]}, {
                "$set": {
                    "last_value": float(total_seconds(d["last"] - d["start"]))
                }
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
        bulk = db.noc.fm.uptimes.initialize_unordered_bulk_op()
        n = 0
        for d in db.noc.fm.uptimes.find({}):
            bulk.find({"_id": d["_id"]}).update({
                "$set": {
                    "last_value": float(total_seconds(d["last"] - d["start"]))
                }
            })
            n += 1
        if n:
            bulk.execute()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def backwards(self):
        pass
