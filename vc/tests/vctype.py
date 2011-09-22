# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VCType model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ModelTestCase
from noc.vc.models import VCType


class VCTypeModelTestCase(ModelTestCase):
    model = VCType

    data = [
        {
            "name": "Test 1",
            "min_labels": 1,
            "label1_min": 0,
            "label1_max": 15
        },
        
        {
            "name": "Test 2",
            "min_labels": 2,
            "label1_min": 0,
            "label1_max": 15,
            "label2_min": 0,
            "label2_max": 15
        }
    ]
