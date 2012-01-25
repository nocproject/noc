# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.vendor unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class VendorTestCase(RestModelTestCase):
    app = "inv.vendor"

    scenario = [
        {
            "GET": {
                # key: value
                "name": "MyVendor"
            },
            "POST": {
                # key: value
                "name": "MyVendor",
                "is_builtin": False,
                "site": "http://example.com/"
            },
            "PUT": {
                # key: value
                "site": "http://myexample.com/"
            }
        }
    ]
