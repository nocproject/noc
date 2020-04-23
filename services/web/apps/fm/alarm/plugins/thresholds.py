# ---------------------------------------------------------------------
# Thresholds plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import AlarmPlugin


class ThresholdsPlugin(AlarmPlugin):
    name = "thresholds"

    def get_data(self, alarm, config):
        r = {
            "plugins": [("NOC.fm.alarm.plugins.Thresholds", {})],
            "thresholds": alarm.vars.get("thresholds", []),
        }
        return r
