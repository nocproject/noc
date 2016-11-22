# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent_usage


class Script(GetMetricsScript):
    name = "Cisco.IOS.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "Subscribers | IPoE": [
            ("SNMP", "1.3.6.1.4.1.6527.3.1.2.33.1.107.1.65.1", "gauge", 1)
        ],
        "CPU | Usage": [
            ("SNMP", "1.3.6.1.4.1.9.9.109.1.1.1.1.7.1", "gauge", 1)
        ],
        "Memory | Usage": [
            (
                "SNMP",
                [
                    "1.3.6.1.4.1.9.9.48.1.1.1.6.1",
                    "1.3.6.1.4.1.9.9.48.1.1.1.5.1"
                ],
                "gauge",
                percent_usage
            )
        ],
    })

    def collect_profile_metrics(self, metrics):
        if self.has_capability("Cisco | IP | SLA | Probes"):
            pass
