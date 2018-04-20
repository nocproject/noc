# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.language unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import RestModelTestCase


class MainLanguageTestCase(RestModelTestCase):
    app = "main.language"

    scenario = [
        {
            "GET": {
                "name": "Tengwar",
                "native_name": "Quenya"
            },
            "POST": {
                "name": "Tengwar",
                "native_name": "Quenya",
                "is_active": True
            },
            "PUT": {
                "is_active": False
            }
        }
    ]
