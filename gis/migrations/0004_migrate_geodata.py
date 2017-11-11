# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import json
# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import InsertOne
# NOC modules
from south.db import db
# NOC modules
from noc.lib.nosql import get_db, ObjectId


class Migration(object):
    def forwards(self):
        if db.execute(
            """
            select count(*) from pg_class where relname='gis_geodata'
            """
        )[0][0] == 0:
            return  # No PostGIS
        c = get_db().noc.geodata
        bulk = []
        for layer, label, object, data in db.execute("""
            SELECT layer, label, object, ST_AsGeoJSON(data)
            FROM gis_geodata
        """):
            data = json.loads(data)
            bulk += [InsertOne({
                 "layer": ObjectId(layer),
                 "object": ObjectId(object),
                 "label": label,
                 "data": data
            })]
        if bulk:
            print("Commiting changes to database")
            try:
                c.bulk_write(bulk)
                print("Database has been synced")
            except BulkWriteError as e:
                print("Bulk write error: '%s'", e.details)
                print("Stopping check")
        # Leave table for further analisys
        # db.drop_table("gis_geodata")

    def backwards(self):
        pass
