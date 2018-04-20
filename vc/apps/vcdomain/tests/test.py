# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc.vcdomain unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready yet")
class VCDomainTestCase(RestModelTestCase):
    app = "vc.vcdomain"

    scenario = [
        {
            "GET": {
                "name": "My Domain"
            },
            "POST": {
                # key: value
            },
            "PUT": {
                # key: value
            }
        }
    ]
