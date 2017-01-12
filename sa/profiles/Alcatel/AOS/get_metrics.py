# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_metrics
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
            ("SNMP", "1.3.6.1.4.1.6486.800.1.2.1.16.1.1.1.13.0", "gauge", 1)
        ],

        "CPU | Usage | 5sec": [
            [
                "SNMP",
                "1.3.6.1.4.1.6486.800.1.2.1.16.1.1.2.1.1.14",
                "gauge", 1, "slot", "%(healthModuleSlot)d"]],
        "CPU | Load | 1min": [
            [
                "SNMP",
                "1.3.6.1.4.1.6486.800.1.2.1.16.1.1.2.1.1.15",
                "gauge", 1, "slot", "%(healthModuleSlot)d"]],
        "Memory | Usage | 5sec": [
            [
                "SNMP",
                "1.3.6.1.4.1.6486.800.1.2.1.16.1.1.2.1.1.10",
                "gauge", 1, "slot", "%(healthModuleSlot)d"]],
        "Memory | Load | 1min": [
            [
                "SNMP",
                "1.3.6.1.4.1.6486.800.1.2.1.16.1.1.2.1.1.11",
                "gauge", 1, "slot", "%(healthModuleSlot)d"]]
    })

    PROFILE_HINTS = {}

    def collect_profile_metrics(self, metrics):
        healthModuleSlot = [0]
        if self.has_capability("Stack | Members"):
            healthModuleSlot = range(1, self.capabilities["Stack | Members"] + 1)
        i = 1
        r = {}
        for ms in healthModuleSlot:
            # r[i] = "%d.%d.%d" % (fi, si, cp)
            r[str(i)] = {"healthModuleSlot": ms}
            i += 1

        self.PROFILE_HINTS["slot"] = r
