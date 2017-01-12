# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "CPU | Usage": [
            ("SNMP", "1.3.6.1.4.1.2011.2.23.1.18.1.3.0", "gauge", 1)
        ],
        "Memory | Usage": [
            (
                "SNMP",
                [
                    "1.3.6.1.4.1.2011.6.1.2.1.1.3.65536",
                    "1.3.6.1.4.1.2011.6.1.2.1.1.2.65536",
                ],
                "gauge",
                percent
            )
        ],
        "CPU | Usage | 5sec": [
            (
                "SNMP",
                "1.3.6.1.4.1.2011.6.3.4.1.2",
                "gauge", 1, "slot", "%(hwFrameIndex)d.%(hwSlotIndex)d.%(hwCpuDevIndex)d")],
        "CPU | Load | 1min": [
            (
                "SNMP",
                "1.3.6.1.4.1.2011.6.3.4.1.3",
                "gauge", 1, "slot", "%(hwFrameIndex)d.%(hwSlotIndex)d.%(hwCpuDevIndex)d")],
        "CPU | Load | 5min": [
            (
                "SNMP",
                "1.3.6.1.4.1.2011.6.3.4.1.4",
                "gauge", 1, "slot", "%(hwFrameIndex)d.%(hwSlotIndex)d.%(hwCpuDevIndex)d")],
        "Memory | Usage | 5sec": [
            (
                "SNMP",
                [
                    "1.3.6.1.4.1.2011.6.3.5.1.1.3",
                    "1.3.6.1.4.1.2011.6.3.5.1.1.2",
                ],
                "gauge",
                percent,
                "stackmember", "%(hwFrameIndex)d.%(hwSlotIndex)d.%(hwCpuDevIndex)d",
            )
        ],
    })

    PROFILE_HINTS = {}

    def collect_profile_metrics(self, metrics):
        hwFrameIndex = [0]
        hwSlotIndex = [0]
        hwCpuDevIndex = [0]
        if self.has_capability("Stack | Members"):
            hwSlotIndex = range(0, self.capabilities["Stack | Members"])
        i = 0
        r = {}
        for fi in hwFrameIndex:
            for si in hwSlotIndex:
                for cp in hwCpuDevIndex:
                    # r[i] = "%d.%d.%d" % (fi, si, cp)
                    r[str(i)] = {"hwFrameIndex": fi, "hwSlotIndex": si, "hwCpuDevIndex": cp}
                    i += 1

        self.PROFILE_HINTS["slot"] = r
