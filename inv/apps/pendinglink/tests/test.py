# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.pendinglink unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready")
class PendingLinkCheckTestCase(RestModelTestCase):
    app = "inv.pendinglink"

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
