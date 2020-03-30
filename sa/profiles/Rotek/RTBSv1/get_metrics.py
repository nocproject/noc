# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Rotek.RTBSv1.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.validators import is_ipv4


class Script(GetMetricsScript):
    name = "Rotek.RTBSv1.get_metrics"

    @metrics(["Check | Result"], volatile=False, access="C")  # CLI version
    def get_avail_metrics(self, metrics):
        if not self.credentials["path"]:
            return
        self.logger.info("Collecting Check metrics: %s", metrics)
        metric = metrics[0]
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip)
                self.set_metric(
                    id=metric.id,
                    metric="Check | Result",
                    path=("ping", ip),
                    value=bool(result["success"]),
                    multi=True,
                )

    @metrics(["Check | RTT"], volatile=False, access="C")  # CLI version
    def get_avail_rtt_metrics(self, metrics):
        if not self.credentials["path"]:
            return
        self.logger.info("Collecting Check metrics: %s", metrics)
        metric = metrics[0]
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip)
                if result["success"]:
                    self.set_metric(
                        id=metric.id,
                        metric="Check | RTT",
                        path=("ping", ip),
                        value=bool(result["success"]),
                    )
