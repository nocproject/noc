# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.ignoreeventroules unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready")
class IgnoreEventRulesTestCase(RestModelTestCase):
    app = "fm.ignoreeventrule"

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
