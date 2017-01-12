# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent_usage


class Script(GetMetricsScript):
    name = "Juniper.JUNOSe.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "Subscribers | IPoE": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.18.1.5.11.0", "counter", 1)
        ],
        "Subscribers | PPP": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.11.1.7.7.0", "counter", 1)
        ],
        "Subscribers | L2TP": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.35.1.1.2.10.0", "gauge", 1)
        ],
        "Environment | Temperature": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.2.1.9.4.1.3.1", "counter", 1)
        ],
    })
