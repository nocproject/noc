# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# upgrade uptime
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        bulk = []
        for d in db.noc.fm.uptimes.find({}):
            bulk += [
                UpdateOne(
                    {"_id": d["_id"]},
                    {"$set": {"last_value": float((d["last"] - d["start"]).total_seconds())}},
                )
            ]
        if bulk:
            print("Commiting changes to database")
            try:
                db.noc.fm.uptimes.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print(("Bulk write error: '%s'", e.details))
                print("Stopping check")
