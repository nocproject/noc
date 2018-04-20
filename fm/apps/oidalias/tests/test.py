# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.oidalias unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class OIDAliasTestCase(RestModelTestCase):
    app = "fm.oidalias"

    scenario = [
        {
            "GET": {
                "rewrite_oid": "1.2.3.4.5.6.7.8.9.10"
            },
            "POST": {
                "rewrite_oid": "1.2.3.4.5.6.7.8.9.10",
                "to_oid": "1.2.3.4.5.6.7.8.9.11"
            },
            "PUT": {
                "rewrite_oid": "1.2.3.4.5.6.7.8.9.10",
                "to_oid": "1.2.3.4.5.6.7.8.9.15",
                "description": "Test"
            }
        }
    ]
