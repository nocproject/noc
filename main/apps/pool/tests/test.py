# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.pool unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready")
class PoolTestCase(RestModelTestCase):
    app = "main.pool"

    scenario = [
        {
            "GET": {
                # key: value
            },
            "POST": {
                # key: value
            },
            "PUT": {
                # key: value
            }
        }
    ]
