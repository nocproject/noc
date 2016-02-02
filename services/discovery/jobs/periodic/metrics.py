# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric collector
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
## Third-party modules
import cachetools
## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface


class MetricsCheck(DiscoveryCheck):
    """
    MAC discovery
    """
    name = "metrics"
    required_script = "get_metrics"

    def handler(self):
        def q(s):
            return s.replace(" ", "\\ ").replace(",", "\\,")

        def q_tags(t):
            return ",".join(q(t[s]) for s in sorted(t))

        self.logger.info("Collecting metrics")
        # Get interface configurations
        hints = {
            "ifindexes": {}
        }
        metrics = {}
        for i in Interface._get_collection().find({
            "managed_object": self.object.id,
            "type": "physical"
        }, {
            "name": 1,
            "ifindex": 1,
            "profile": 1
        }):
            ipr = self.interface_profile_metrics_cache[i["profile"]]
            if not ipr:
                continue
            if i["ifindex"]:
                hints["ifindexes"][i["name"]] = i["ifindex"]
            for metric in ipr:
                if metric in metrics:
                    metrics[metrics]["interfaces"] += [i["name"]]
                else:
                    metrics[metrics] = {
                        "interfaces": [i["name"]],
                        "scope": "i"
                    }
        # Collect metrics
        self.logger.debug("Collecting metrics: %s hints: %s",
                          metrics, hints)
        result = self.object.scripts.get_metrics(
            metrics=metrics,
            hints=hints
        )
        if not result:
            self.logger.info("No metrics found")
            return
        # Process result
        batch = []
        for m in result:
            batch += [
                "%s,%s value=%s %s" % (
                    q(m["name"]),
                    q_tags(m["tags"]),
                    m["value"],
                    m["ts"]
                )
            ]
        self.logger.info("METRICS BATCH: %s", batch)
        # @todo: Check thresholds
        # @todo: Send FM alarms
        # @todo: Send metrics

    @classmethod
    def get_interface_profile_metrics(cls, p_id):
        with cls.interface_profile_metrics_lock:
            r = {}
            ipr = InterfaceProfile.objects.filter(id=p_id).first()
            for m in ipr.metrics:
                if not m.is_active:
                    continue
                r[m.metric_type.name] = {
                    "low_error": m.low_error,
                    "low_warn": m.low_warn,
                    "high_warn": m.high_warn,
                    "high_error": m.high_error
                }

    interface_profile_metrics_lock = threading.Lock()
    interface_profile_metrics_cache = cachetools.TTLCache(
        1000, 60, missing=get_interface_profile_metrics
    )
