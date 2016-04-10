# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Siklu.EH.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "Siklu.EH.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "Environment | Voltage": [
            ("SNMP", "1.3.6.1.4.1.31926.1.1.0", "gauge", 1)
        ],
        "Environment | Temperature": [
            ("SNMP", "1.3.6.1.4.1.31926.1.2.0", "gauge", 1)
        ],
        "Radio | CINR": [
            ("SNMP", "1.3.6.1.4.1.31926.2.1.1.18.1", "gauge", 1)
        ],
        "Radio | RSSI": [
            ("SNMP", "1.3.6.1.4.1.31926.2.1.1.19.1", "gauge", 1)
        ]

    })
