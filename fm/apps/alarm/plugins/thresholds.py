# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Thresholds plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import AlarmPlugin


class ThresholdsPlugin(AlarmPlugin):
    name = "validation"

    def get_data(self, alarm, config):
        r = {
            "plugins": [("NOC.fm.alarm.plugins.Thresholds", {})],
            "thresholds": alarm.vars.get("thresholds", [])
        }
        return r
