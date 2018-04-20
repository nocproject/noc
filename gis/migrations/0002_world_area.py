# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

from south.db import db
from noc.lib.nosql import get_db

class Migration:

    def forwards(self):
        areas = get_db().noc.gis.areas
        if not areas.find({"name": "World"}).count():
            areas.insert({
                "name": "World",
                "is_active": True,
                "min_zoom": 0,
                "max_zoom": 5,
                "SW": [-180.0, -90.0],
                "NE": [179.999999, 89.999999]
<<<<<<< HEAD
            })

    def backwards(self):
        pass
=======
            }, safe=True)

    def backwards(self):
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
