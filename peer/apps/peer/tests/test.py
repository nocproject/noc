# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.peer unittest
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest

@unittest.skip("Not ready")
class PeerTestCase(RestModelTestCase):
    app = "peer.peer"

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

