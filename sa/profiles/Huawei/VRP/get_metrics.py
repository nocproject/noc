# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "CPU | Usage": [
            ("SNMP", "1.3.6.1.4.1.2011.2.23.1.18.1.3.0", "gauge", 1)
        ],
        "Memory | Total": [
            ("SNMP", "1.3.6.1.4.1.2011.6.1.2.1.1.2.65536", "gauge", 1)
        ],
        "Memory | Used": [
            ("SNMP", "1.3.6.1.4.1.2011.6.1.2.1.1.3.65536", "gauge", 1)
        ]

    })
