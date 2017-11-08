# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.lib.text import parse_kv
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "Cisco.IOS.get_metrics"

    ALL_SLA_METRICS = {"SLA | ICMP RTT", "SLA | JITTER", "SLA | UDP RTT"}

    def collect_profile_metrics(self, metrics):
        if self.has_capability("Cisco | IP | SLA | Probes"):
            self.logger.debug("Merics %s" % metrics)
            if self.ALL_SLA_METRICS.intersection(set(m.metric for m in metrics)):
                # check
                self.collect_ip_sla_metrics(metrics)

    def collect_ip_sla_metrics(self, metrics):
        # if not (self.ALL_SLA_METRICS & set(metrics)):
        #    return  # NO SLA metrics requested
        ts = self.get_ts()
        m = self.get_ip_sla_metrics()
        for bv in metrics:
            if bv.metric in self.ALL_SLA_METRICS:
                id = tuple(bv.path + [bv.metric])
                if id in m:
                    self.set_metric(
                        id=bv.id,
                        metric=bv.metric,
                        value=m[id],
                        ts=ts,
                        path=bv.path,
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
        metric_map = {"ipsla operation id": "name",
                      "latest rtt": "rtt",
                      "source to destination jitter min/avg/max": "sd_jitter",
                      "destination to source jitter min/avg/max": "ds_jitter",
                      "number of rtt": "num_rtt"}

        r_v = self.rx_ipsla_probe.split(v)
        if len(r_v) < 3:
            return {}
        # r = defaultdict(dict)
        r = {}

        for probe_id, data in zip(r_v[1::2], r_v[2::2]):
            p = parse_kv(metric_map, data)
            if "rtt" in p:
                # Latest RTT: 697 milliseconds
                rtt = p["rtt"].split()[0]
                try:
                    r[("", probe_id, "SLA | UDP RTT")] = float(rtt) * 1000
                except ValueError:
                    pass
            if "sd_jitter" in p:
                # Source to Destination Jitter Min/Avg/Max: 0/8/106 milliseconds
                jitter = p["sd_jitter"].split()[0].split("/")[1]
                r[("", probe_id, "SLA | JITTER")] = float(jitter) * 1000
        return r
