# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.ignorepattern unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Not ready")
class IgnorePatternTestCase(RestModelTestCase):
    app = "fm.ignorepattern"

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
