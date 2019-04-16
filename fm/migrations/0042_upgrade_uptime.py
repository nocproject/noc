# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# upgrade uptime
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Python modules
from __future__ import print_function
# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
# NOC modules
from noc.lib.nosql import get_db
from noc.lib.dateutils import total_seconds


class Migration(object):
    def forwards(self):
        db = get_db()
        bulk = []
        for d in db.noc.fm.uptimes.find({}):
            bulk += [
                UpdateOne({
                    "_id": d["_id"]
                }, {"$set": {
                    "last_value": float(total_seconds(d["last"] - d["start"]))
                }})
            ]
        if bulk:
            print("Commiting changes to database")
            try:
                db.noc.fm.uptimes.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print(("Bulk write error: '%s'", e.details))
                print("Stopping check")

    def backwards(self):
        pass
