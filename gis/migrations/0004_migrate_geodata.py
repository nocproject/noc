# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import json
## Third-party modules
from south.db import db
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        bulk = []
=======
        bulk = c.initialize_unordered_bulk_op()
        n = 0
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        for layer, label, object, data in db.execute("""
            SELECT layer, label, object, ST_AsGeoJSON(data)
            FROM gis_geodata
        """):
            data = json.loads(data)
<<<<<<< HEAD
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
=======
            bulk.insert({
                 "layer": ObjectId(layer),
                 "object": ObjectId(object),
                 "label": label,
                 "data": data
            })
            n += 1
        if n:
            bulk.execute()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Leave table for further analisys
        # db.drop_table("gis_geodata")

    def backwards(self):
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
