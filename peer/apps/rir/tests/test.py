# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.rir unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class RIRTestCase(RestModelTestCase):
    app = "peer.rir"

    scenario = [
        {
            "GET": {
                "name": "NOC RIR"
            },
            "POST": {
                "name": "NOC RIR",
                "whois": "nocproject.org"
            },
            "PUT": {
                "name": "NOC RIR",
                "whois": "whois.nocproject.org"
            }
        }
    ]
