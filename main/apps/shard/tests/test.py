# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.shard unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class ShardTestCase(RestModelTestCase):
    app = "main.shard"

    scenario = [
        {
            "GET": {
                "name": "Test"
            },
            "POST": {
                "name": "Test",
                "is_active": False,
                "description": "Testing Shard"
            },
            "PUT": {
                "is_active": True
            }
        }
    ]
