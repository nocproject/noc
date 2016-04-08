# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "EdgeCore.ES.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "CPU | Usage": [
            ("SNMP", "1.3.6.1.4.1.259.6.10.94.1.39.2.1", "gauge", 1)
        ],
        "Memory | Usage": [
            ("SNMP", "1.3.6.1.4.1.259.6.10.94.1.39.3.2", "gauge", 1)
        ]

    })
