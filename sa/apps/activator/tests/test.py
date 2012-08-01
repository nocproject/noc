# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.activator unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready")
class ActivatorTestCase(RestModelTestCase):
    app = "sa.activator"

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
