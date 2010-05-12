# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vrf Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelTestCase
from noc.ip.models import *

class VRFTestCase(ModelTestCase):
    model=VRF
    def get_data(self):
        return [
            {
                "name":"VRF1",
                "vrf_group_id" : 1,
                "rd": "65000:1",
            },
            {
                "name":"VRF2",
                "vrf_group_id" : 1,
                "rd": "65000:2",
            },
            {
                "name":"VRF3",
                "vrf_group_id" : 1,
                "rd": "65000:3",
            }
        ]
    ##
    ## Additional VRF testing
    ##
    def object_test(self,o):
        o.prefix()
        o.prefixes()
        o.all_prefixes()
        o.all_addresses()
