# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## Rotek.RTBS.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.lib.mib import mib
from noc.core.script.metrics import percent


class Script(GetMetricsScript):
    name = "Rotek.RTBS.get_metrics"

class PlatformRule(OIDRule):
    name = "platform"

    def iter_oids(self, script, cfg):
        ver = script.snmp.get("1.3.6.1.2.1.1.2.0")
        #check sysObjectID
        obj = ver.split(".")[-1]
        oid = mib[self.expand(self.oid, {"platform": obj, "ifIndex": cfg.ifindex})]
        if oid:
            yield oid, self.type, self.scale, cfg.path
