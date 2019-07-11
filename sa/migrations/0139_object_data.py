# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# object data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        uc = self.mongo_db["noc.objectuplinks"]
        dc = self.mongo_db["noc.objectdata"]
        bulk = []
        for d in uc.find():
            bulk += [InsertOne({"_id": d["_id"], "uplinks": d.get("uplinks", [])})]
        if bulk:
            print("Commiting changes to database")
            try:
                dc.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print(("Bulk write error: '%s'", e.details))
                print("Stopping check")
