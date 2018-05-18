# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Rotek.RTBS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from .oidrules.platform import PlatformRule
from noc.lib.validators import is_ipv4


class Script(GetMetricsScript):
    name = "Rotek.RTBS.get_metrics"
    OID_RULES = [
        PlatformRule
    ]
    CHECKS = set(["Check | Avail"])

    def collect_profile_metrics(self, metrics):
        self.logger.debug("Merics %s" % metrics)
        if self.CHECKS.intersection(set(m.metric for m in metrics)) and self.credentials.get("path"):
            # check
            self.collect_avail_metrics(metrics)

    def collect_avail_metrics(self, metrics):
        ts = self.get_ts()
        m = self.get_avail_metrics()
        for bv in metrics:
            if bv.metric in self.CHECKS:
                for slot in m:
                    self.set_metric(
                        id=bv.id,
                        metric=bv.metric,
                        value=m[slot],
                        ts=ts,
                        path=slot[:-1]
                    )

    def get_avail_metrics(self):
        r = {}
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip)
                r[("ping", ip, "Check | Result")] = bool(result["success"])
                if result["success"]:
                    r[("ping", ip, "Check | RTT")] = float(result["avg"])
        return r
