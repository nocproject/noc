# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HTTP Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes import *
import time,random
##
## Test probe
## Generate 3 random sequences
##
class TestProbe(Probe):
    name="test"
    parameters = {
        "param1" : {},
        "param2" : {
            "threshold" : {
                "warn" : { "high" : 800 },
                "fail" : { "high" : 900 }
            }
        },
        "param3" : {
            "threshold" : {
                "fail" : { "low" : 100 }
            }
        },
        "param4" : {
            "type" : "counter",
        }
    }
    def __init__(self,daemon,probe_name,config):
        super(TestProbe,self).__init__(daemon,probe_name,config)
        self.ww=0
    def on_start(self):
        for service in self.services:
            if random.random()<0.25: # Simulate Fail
                self.set_result(service,PR_FAIL,"Test Failure")
            else:
                for i in range(1,4):
                    self.set_data(service,"param%d"%i, random.random()*1000-500)
                self.set_result(service,PR_OK)
            self.set_data(service,"param4",self.ww)
        self.ww=(self.ww+1000000000)&0xFFFFFFFF # Simulate wrapping
        self.exit()
