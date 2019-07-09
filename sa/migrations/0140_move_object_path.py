# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# move object path
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
        uc = self.mongo_db["noc.cache.objectpaths"]
        dc = self.mongo_db["noc.objectdata"]
        bulk = []
        for d in uc.find():
            bulk += [
                UpdateOne(
                    {"_id": d["_id"]},
                    {
                        "$set": {
                            "adm_path": d.get("adm_path", []),
                            "segment_path": d.get("segment_path", []),
                            "container_path": d.get("container_path", []),
                        }
                    },
                    upsert=True,
                )
            ]
        if bulk:
            print("Commiting changes to database")
            try:
                dc.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print(("Bulk write error: '%s'", e.details))
                print("Stopping check")
