# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# migrate geodata
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import json

# Third-party modules
import bson
from pymongo.errors import BulkWriteError
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if (
            self.db.execute(
                """
                select count(*) from pg_class where relname='gis_geodata'
                """
            )[0][0]
            == 0
        ):
            return  # No PostGIS
        c = self.mongo_db.noc.geodata
        bulk = []
        for layer, label, object, data in self.db.execute(
            """
            SELECT layer, label, object, ST_AsGeoJSON(data)
            FROM gis_geodata
        """
        ):
            data = json.loads(data)
            bulk += [
                InsertOne(
                    {
                        "layer": bson.ObjectId(layer),
                        "object": bson.ObjectId(object),
                        "label": label,
                        "data": data,
                    }
                )
            ]
        if bulk:
            print("Commiting changes to database")
            try:
                c.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print(("Bulk write error: '%s'", e.details))
                print("Stopping check")
