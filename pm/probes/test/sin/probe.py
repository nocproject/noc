## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test sine function
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import math
## NOC modules
from noc.pm.probes.base import Probe, metric


class SinProbe(Probe):
    TITLE = "Sin"
    DESCRIPTION = "Sample sine function"
    TAGS = ["test"]
    CONFIG_FORM = [
        {
            "name": "Period",
            "xtype": "numberfield",
            "fieldLabel": "Period",
            "allowBlank": False,
            "defaultValue": 60
        },
        {
            "name": "Scale",
            "xtype": "numberfield",
            "fieldLabel": "Scale",
            "allowBlank": False,
            "defaultValue": 1
        }
    ]

    @metric("Test | Sin",
            preference=metric.PREF_COMMON, convert=metric.NONE)
    def get_sin(self, scale=1.0, period=60):
        return math.sin(time.time() * 2 * math.pi / period) * scale
