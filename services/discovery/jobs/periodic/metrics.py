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


MAX31 = 0x7FFFFFFFL
MAX32 = 0xFFFFFFFFL
MAX64 = 0xFFFFFFFFFFFFFFFFL


def get_interface_profile_metrics(p_id):
    with interface_profile_metrics_lock:
        r = {}
        ipr = InterfaceProfile.objects.filter(id=p_id).first()
        if not ipr:
            return None
        for m in ipr.metrics:
            if not m.is_active:
                continue
            r[m.metric_type.name] = {
                "low_error": m.low_error,
                "low_warn": m.low_warn,
                "high_warn": m.high_warn,
                "high_error": m.high_error
            }
        return r

interface_profile_metrics_lock = threading.Lock()


class MetricsCheck(DiscoveryCheck):
    """
    MAC discovery
    """
    name = "metrics"
    required_script = "get_metrics"

    interface_profile_metrics_cache = cachetools.TTLCache(
        1000, 60, missing=get_interface_profile_metrics
    )
    # Last counter values
    counter_values = {}
    counter_lock = threading.Lock()

    def handler(self):
        def q(s):
            return s.replace(" ", "\\ ").replace(",", "\\,")

        def q_tags(t):
            return ",".join("%s=%s" % (q(s), q(t[s])) for s in sorted(t))

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
                    metrics[metric]["interfaces"] += [i["name"]]
                else:
                    metrics[metric] = {
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
        # Build output batch
        batch = []
        with self.counter_lock:
            for m in result:
                key = "%s,%s" % (q(m["name"]), q_tags(m["tags"]))
                if m["type"] == "counter":
                    # Resolve counter
                    r = self.counter_values.get(key)
                    # Store value
                    self.counter_values[key] = (m["ts"], m["value"])
                    if r:
                        # Calculate counter
                        m["value"] = self.convert_counter(
                            m["ts"], m["value"],
                            r[0], r[1]
                        )
                    else:
                        continue  # Skip the step
                batch += [
                    "%s value=%s %s" % (
                        key,
                        m["value"] * m["scale"],
                        m["ts"]
                    )
                ]
        self.logger.info("METRICS BATCH: %s", batch)
        # @todo: Check thresholds
        # @todo: Send FM alarms
        # @todo: Send metrics

    @staticmethod
    def convert_counter(new_ts, new_value, old_ts, old_value):
        """
        Calculate value from counter, gently handling overflows
        """
        if new_value < old_value:
            # Counter decreased, either due wrap or stepback
            if old_value <= MAX31:
                mc = MAX31
            elif old_value <= MAX32:
                mc = MAX32
            else:
                mc = MAX64
            # Direct distance
            d_direct = old_value - new_value
            # Wrap distance
            d_wrap = new_value + (mc - old_value)
            if d_direct < d_wrap:
                # Possible counter stepback, return old_value
                return old_value
            else:
                # Counter wrap
                return float(d_wrap) / ((float(new_ts) - float(old_ts)) / 1000000.0)
        else:
            return (float(new_value) - float(old_value)) / ((float(new_ts) - float(old_ts)) / 1000000.0)
