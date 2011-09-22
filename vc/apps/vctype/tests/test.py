# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc.vctype unittes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import RestModelTestCase


class VCTypeTestCase(RestModelTestCase):
    app = "vc.vctype"

    scenario = [
        {
            "GET": {
                "name": "Test 1"
            },
            "POST": {
                "name": "Test 1",
                "min_labels": 1,
                "label1_min": 0,
                "label1_max": 15
            },
            "PUT": {
                "label1_max": 31
            }
        },

        {
            "GET": {
                "name": "Test 2"
            },
            "POST": {
                "name": "Test 2",
                "min_labels": 2,
                "label1_min": 0,
                "label1_max": 15,
                "label2_min": 0,
                "label2_max": 15
            },
            "PUT": {
                "label1_max": 31
            }
        }
    ]
