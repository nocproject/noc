# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent_usage


class Script(GetMetricsScript):
    name = "Cisco.IOS.get_metrics"

    ALL_SLA_METRICS = set(["SLA | ICMP RTT"])
    SLA_ICMP_RTT = "SLA | ICMP RTT"

    def collect_profile_metrics(self, metrics):
        if self.has_capability("Cisco | IP | SLA | Probes"):
            self.collect_ip_sla_metrics(metrics)

    def collect_ip_sla_metrics(self, metrics):
        if not (self.ALL_SLA_METRICS & set(metrics)):
            return  # NO SLA metrics requested
        ts = self.get_ts()
        m = self.get_ip_sla_metrics()
        if self.SLA_ICMP_RTT in metrics:
            for probe in metrics["SLA | ICMP RTT"]["probes"]:
                if probe in m and "rtt" in m[probe]:
                    self.set_metric(
                        name="SLA | ICMP RTT",
                        value=m[probe]["rtt"],
                        ts=ts,
                        tags={"probe": probe}
                    )

    rx_ipsla_probe = re.compile(
        r"(?:IPSLA operation id:|Round Trip Time \(RTT\) for.+Index)\s+(\d+)",
        re.MULTILINE
    )

    rx_ipsla_latest_rtt = re.compile(
        r"Latest RTT:\s+(\d+)"
    )

    def get_ip_sla_metrics(self):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        v = self.cli("show ip sla statistics")
        r_v = self.rx_ipsla_probe.split(v)
        if len(r_v) < 3:
            return {}
        r = defaultdict(dict)
        for probe_id, data in zip(r_v[1::2], r_v[2::2]):
            match = self.rx_ipsla_latest_rtt.search(data)
            if not match:
                continue
            rtt = match.group(1)
            r[probe_id]["rtt"] = float(rtt) / 1000.0
        return r
