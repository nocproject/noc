# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.ES.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent

#
# Tested on  ES-2024A. works only on firmware 3.90+
# via http://kb.zyxel.com/KB/searchArticle!gwsViewDetail.action?articleOid=012648&lang=EN
#
class Script(GetMetricsScript):
    name = "Zyxel.ZyNOS.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "CPU | Usage": [
            ("SNMP", "1.3.6.1.4.1.890.1.5.8.16.9.7.0", "gauge", 1)
        ],
        "Memory | Usage": [
            ("SNMP", "1.3.6.1.4.1.890.1.5.8.16.124.1.1.5.1", "gauge", 1)
        ]

    })
