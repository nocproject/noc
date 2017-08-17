# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OneAccess.TDRE.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent_usage


class Script(GetMetricsScript):
    name = "OneAccess.TDRE.get_metrics"

    rx_metric = re.compile(
        r"^\s+name = (?P<name>\S+)\s*\n"
        r"^\s+status = run\s*\n"
        r"^\s+ipAddress = .+\n"
        r"^\s+hostName = .+\n"
        r"^\s+sourceIp = .+\n"
        r"^\s+sourceId = .+\n"
        r"^\s+nbrOfTxPackets = .+\n"
        r"^\s+nbrOfRxPackets = .+\n"
        r"^\s+error = .+\n"
        r"^\s+delay = \"(?P<delay>\S+) sec\"\s*\n"
        r"^\s+jitter = \"(?P<jitter>\S+) sec\"\s*\n"
        r"^\s+loss = .+\n"
        r"^\s+lossDelay = .+\n"
        r"^\s+delayMin = .+\n"
        r"^\s+delayAvrg = .+\n"
        r"^\s+delayMax = .+\n"
        r"^\s+jitterNegMax = .+\n"
        r"^\s+jitterAvrg = .+\n"
        r"^\s+jitterPosMax = .+\n",
        re.MULTILINE
    )

    ALL_SLA_METRICS = set(["SLA | ICMP RTT", "SLA | UDP RTT", "SLA | JITTER"])
    SLA_ICMP_RTT = "SLA | ICMP RTT"
    SLA_UDP_RTT = "SLA | UDP RTT"
    SLA_JITTER = "SLA | JITTER"

    def collect_profile_metrics(self, metrics):
        if self.has_capability("OneAccess | IP | SLA | Probes"):
            self.collect_ip_sla_metrics(metrics)
        self.collect_ip_sla_metrics(metrics)

    def collect_ip_sla_metrics(self, metrics):
        if not (self.ALL_SLA_METRICS & set(metrics)):
            return  # NO SLA metrics requested
        ts = self.get_ts()
        probes = self.scripts.get_sla_probes()
        self.cli("SELGRP Performance")
        c = self.cli("GET ip/router/qualityMonitor[]/")
        for match in self.rx_metric.finditer(c):
            name = match.group("name")
            delay = match.group("delay")
            jitter = match.group("jitter")
            if self.SLA_ICMP_RTT in metrics:
                for p in probes:
                    if (
                        p["name"] == name and
                        p["tests"][0]["type"] == "icmp-echo" and
                        name in metrics[self.SLA_ICMP_RTT]["probes"]
                    ):
                        self.set_metric(
                            name=self.SLA_ICMP_RTT,
                            value=float(delay) * 1000000,
                            ts=ts,
                            tags={"probe": name}
                        )
            if self.SLA_UDP_RTT in metrics:
                for p in probes:
                    if (
                        p["name"] == name and
                        p["tests"][0]["type"] == "udp-echo" and
                        name in metrics[self.SLA_UDP_RTT]["probes"]
                    ):
                        self.set_metric(
                            name=self.SLA_UDP_RTT,
                            value=float(delay) * 1000000,
                            ts=ts,
                            tags={"probe": name}
                        )
            if self.SLA_JITTER in metrics:
                for p in probes:
                    if (
                        p["name"] == name and
                        name in metrics[self.SLA_JITTER]["probes"]
                    ):
                        self.set_metric(
                            name=self.SLA_JITTER,
                            value=float(jitter) * 1000000,
                            ts=ts,
                            tags={"probe": name}
                        )
                        break

