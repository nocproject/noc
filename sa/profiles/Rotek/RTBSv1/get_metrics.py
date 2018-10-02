# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Rotek.RTBSv1.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.lib.validators import is_ipv4


class Script(GetMetricsScript):
    name = "Rotek.RTBSv1.get_metrics"

    @metrics(
        ["Check | Result", "Check | RTT"],
        volatile=False,
        access="C"  # CLI version
    )
    def get_avail_metrics(self, metrics):
        if not self.credentials["path"]:
            return
        check_id = 999
        check_rtt = 998
        for m in metrics:
            if m.metric == "Check | Result":
                check_id = m.id
            if m.metric == "Check | RTT":
                check_rtt = m.id
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip)
                self.set_metric(
                    id=check_id,
                    metric="Check | Result",
                    path=("ping", ip),
                    value=bool(result["success"]),
                    multi=True
                )
                if result["success"] and check_rtt != 998:
                    self.set_metric(
                        id=check_rtt,
                        metric="Check | RTT",
                        path=("ping", ip),
                        value=bool(result["success"])
                    )
