# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        areas = get_db().noc.gis.areas
        if not areas.count_documents({"name": "World"}):
            areas.insert({
                "name": "World",
                "is_active": True,
                "min_zoom": 0,
                "max_zoom": 5,
                "SW": [-180.0, -90.0],
                "NE": [179.999999, 89.999999]
            })

    def backwards(self):
        pass
