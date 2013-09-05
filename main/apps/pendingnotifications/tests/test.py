# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.pendingnotifications unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready")
class NotificationTestCase(RestModelTestCase):
    app = "main.pendingnotifications"

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
