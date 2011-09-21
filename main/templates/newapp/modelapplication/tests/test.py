# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## {{module}}.{{app}} unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-{{year}} The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class {{model}}TestCase(RestModelTestCase):
    app = "{{module}}.{{app}}"

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
