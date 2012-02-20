# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.pyrule unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class PyRuleTestCase(RestModelTestCase):
    app = "main.pyrule"

    scenario = [
        {
            "GET": {
                "name": "my_test_pyrule"
            },
            "POST": {
                "name": "my_test_purule",
                "interface": "IEventTrigger",
                "description": "Testing pyRule",
                "text": "@pyrule\ndef myrule(event):\n    pass\n",
                "is_builtin": False
            },
            "PUT": {
                "text": "@pyrule\ndef myrule(event):\n    s = 1\n    pass\n",
            }
        }
    ]
