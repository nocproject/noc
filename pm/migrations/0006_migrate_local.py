# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# migrate local
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function

# Third-party modules
from bson.binary import Binary
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        phash = {}
        db = self.mongo_db
        metrics = db.noc.ts.metrics
        bulk = []
        for m in metrics.find({}).sort("name", 1):
            phash[m["name"]] = m["hash"]
            if "." in m["name"]:
                pn = ".".join(m["name"].split(".")[:-1])
                parent = phash[pn]
            else:
                parent = Binary("\x00" * 8)
            bulk += [
                UpdateOne(
                    {"_id": m["_id"]},
                    {"$set": {"local": m["name"].split(".")[-1], "parent": parent}},
                )
            ]
        if bulk:
            print("Commiting changes to database")
            try:
                metrics.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print(("Bulk write error: '%s'", e.details))
                print("Stopping check")
