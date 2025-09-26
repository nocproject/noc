# ---------------------------------------------------------------------
# DiagnosticPlugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.fm.models.alarmdiagnostic import AlarmDiagnostic
from .base import AlarmPlugin


class DiagnosticPlugin(AlarmPlugin):
    name = "diagnostic"

    def get_data(self, alarm, config):
        d = AlarmDiagnostic.get_diagnostics(alarm)
        if d:
            for x in d:
                x["timestamp"] = x["timestamp"].isoformat()
            return {"plugins": [("NOC.fm.alarm.plugins.Diagnostic", {})], "diagnostic": d}
        return {}
