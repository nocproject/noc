# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.mimetype unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import RestModelTestCase


class MIMETypeTestCase(RestModelTestCase):
    app = "main.mimetype"

    scenario = [
        {
            "GET": {
                "extension": ".noc",
                "mime_type": "application/noc-type"
            },
            "POST": {
                "extension": ".noc",
                "mime_type": "application/noc-type"
            },
            "PUT": {
                "mime_type": "application/x-noc-type"
            }
        }
    ]
