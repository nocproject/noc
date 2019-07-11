# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Thresholds plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

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
