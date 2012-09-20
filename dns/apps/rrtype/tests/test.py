# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## dnszonerecordtype Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready")
class RRTestCase(RestModelTestCase):
    app = "dns.rrtype"

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

