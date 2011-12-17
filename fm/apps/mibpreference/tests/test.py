# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.mibpreference unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class MIBPreferenceTestCase(RestModelTestCase):
    app = "fm.mibpreference"

    scenario = [
        {
            "GET": {
                "mib": "MY-MIB"
            },
            "POST": {
                "mib": "MY-MIB",
                "preference": 70721
            },
            "PUT": {
                "preference": 70722
            }
        }
    ]
