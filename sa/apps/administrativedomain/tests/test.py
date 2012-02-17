# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.administrativedomain unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class AdministrativeDomainTestCase(RestModelTestCase):
    app = "sa.administrativedomain"

    scenario = [
        {
            "GET": {
                "name": "Test"
            },
            "POST": {
                "name": "Test",
                "description": "Test"
            },
            "PUT": {
                "description": "Test Domain"
            }
        }
    ]
