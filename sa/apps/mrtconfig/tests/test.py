# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.mrtconfig unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest


@unittest.skip("Broken")
class MRTConfigTestCase(RestModelTestCase):
    app = "sa.mrtconfig"

    fixtures = ["selector.json", "pyrule.json"]

    scenario = [
        {
            "GET": {
                "name": "mytask"
            },
            "POST": {
                "name": "mytask",
                "description": "Testing Task",
                "is_active": True,
                "permission_name": "run_mytask",
                "selector__name": "My Test Selector",
                "reduce_pyrule__name": "My Test pyRule",
                "map_script": "get_version",
                "timeout": 0
            },
            "PUT": {
                "is_active": False
            }
        }
    ]
