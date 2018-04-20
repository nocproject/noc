# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.commandsnippet unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase, unittest

@unittest.skip("Not ready")
class CommandSnippetTestCase(RestModelTestCase):
    app = "sa.commandsnippet"

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

