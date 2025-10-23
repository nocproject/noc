# ---------------------------------------------------------------------
# OneAccess.TDRE.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


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
        re.MULTILINE,
    )

    ALL_SLA_METRICS = {"SLA | ICMP RTT", "SLA | UDP RTT", "SLA | JITTER"}
    SLA_ICMP_RTT = "SLA | ICMP RTT"
    SLA_UDP_RTT = "SLA | UDP RTT"
    SLA_JITTER = "SLA | JITTER"

    def collect_profile_metrics(self, metrics):
        if self.has_capability("OneAccess | IP | SLA | Probes"):
            self.logger.debug("Merics %s" % metrics)
            if self.ALL_SLA_METRICS.intersection({m.metric for m in metrics}):
                self.collect_ip_sla_metrics(metrics)

    def collect_ip_sla_metrics(self, metrics):
        # if not (self.ALL_SLA_METRICS & set(metrics)):
        #    return  # NO SLA metrics requested
        ts = self.get_ts()
        m = self.get_ip_sla_metrics()
        for bv in metrics:
            if bv.metric in self.ALL_SLA_METRICS:
                id = (*bv.labels, bv.metric)
                if id in m:
                    self.set_metric(
                        id=bv.id, metric=bv.metric, value=m[id], ts=ts, labels=bv.labels
                    )

    def get_ip_sla_metrics(self):
        r = {}
        self.cli("SELGRP Performance")
        c = self.cli("GET ip/router/qualityMonitor[]/")
        for match in self.rx_metric.findall(c):
            r[("", match[0], "SLA | UDP RTT")] = float(match[1]) * 1000000
            r[("", match[0], "SLA | JITTER")] = float(match[2]) * 1000000
        return r
