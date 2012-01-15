# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.area unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class AreaTestCase(RestModelTestCase):
    app = "gis.area"

    scenario = [
        {
            "GET": {
                "name": "Moscow2012"
            },
            "POST": {
                "name": "Moscow2012",
                "is_active": True,
                "min_zoom": 0,
                "max_zoom": 18,
                "NE": [37.97562, 56.05624],
                "SW": [37.11831, 55.42577]
            },
            "PUT": {
                "name": "Moscow2012",
                "min_zoom": 17
            }
        }
    ]
