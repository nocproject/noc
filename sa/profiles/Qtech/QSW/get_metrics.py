# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_metrics import \
    Script as GetMetricsScript
from noc.core.script.metrics import percent


class Script(GetMetricsScript):
    name = "Qtech.QSW.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "CPU | Usage": [
            ("SNMP", "1.3.6.1.4.1.27514.100.1.11.10.0", "gauge", 1)
        ],
        "Memory | Used": [
            (
                "SNMP",
                [
                    "1.3.6.1.4.1.27514.100.1.11.7.0",
                    "1.3.6.1.4.1.27514.100.1.11.6.0"
                ],
                "gauge",
                percent
            )
        ]

    })
