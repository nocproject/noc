# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DiagnosticPlugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.template import Template, Context
# NOC modules
from base import AlarmPlugin
from noc.fm.models.alarmdiagnostic import AlarmDiagnostic


class DiagnosticPlugin(AlarmPlugin):
    name = "diagnostic"

    def get_data(self, alarm, config):
        d = AlarmDiagnostic.get_diagnostics(alarm)
        if d:
            for x in d:
                x["timestamp"] = x["timestamp"].isoformat()
            return {
                "plugins": [("NOC.fm.alarm.plugins.Diagnostic", {})],
                "diagnostic": d
            }
        else:
            return {}
