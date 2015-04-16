# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import json
## Third-party modules
from south.db import db
## NOC modules
from noc.lib.nosql import get_db, ObjectId


class Migration(object):
    def forwards(self):
        c = get_db().noc.geodata
        bulk = c.initialize_unordered_bulk_op()
        n = 0
        for layer, label, object, data in db.execute("""
            SELECT layer, label, object, ST_AsGeoJSON(data)
            FROM gis_geodata
        """):
            data = json.loads(data)
            bulk.insert({
                 "layer": ObjectId(layer),
                 "object": ObjectId(object),
                 "label": label,
                 "data": data
            })
            n += 1
        if n:
            bulk.execute()
        # db.drop_table("gis_geodata")

    def backwards(self):
        pass