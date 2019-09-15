# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.text import parse_kv
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Cisco.IOS.get_metrics"

    rx_ipsla_probe = re.compile(
        r"(?:IPSLA operation id:|Round Trip Time \(RTT\) for.+Index)\s+(\d+)", re.MULTILINE
    )

    rx_ipsla_latest_rtt = re.compile(r"Latest RTT:\s+(\d+)")

    """
    RTT Values:
        Number Of RTT: 1000             RTT Min/Avg/Max: 73/74/75 milliseconds
    Latency one-way time:
        Number of Latency one-way Samples: 1000
        Source to Destination Latency one way Min/Avg/Max: 36/36/38 milliseconds
        Destination to Source Latency one way Min/Avg/Max: 37/37/39 milliseconds
    Jitter Time:
        Number of SD Jitter Samples: 999
        Number of DS Jitter Samples: 999
        Source to Destination Jitter Min/Avg/Max: 0/1/2 milliseconds
        Destination to Source Jitter Min/Avg/Max: 0/1/2 milliseconds
    """

    @metrics(
        ["SLA | JITTER", "SLA | UDP RTT"],
        has_capability="Cisco | IP | SLA | Probes",
        volatile=False,
        access="C",  # CLI version
    )
    def get_ip_sla_udp_jitter_metrics_cli(self, metrics):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        setup_metrics = {
            tuple(m.path): m.id for m in metrics if m.metric in {"SLA | JITTER", "SLA | UDP RTT"}
        }
        v = self.cli("show ip sla statistics")
        metric_map = {
            "ipsla operation id": "name",
            "latest rtt": "rtt",
            "source to destination jitter min/avg/max": "sd_jitter",
            "destination to source jitter min/avg/max": "ds_jitter",
            "number of rtt": "num_rtt",
        }
        r_v = self.rx_ipsla_probe.split(v)
        if len(r_v) < 3:
            return {}

        for probe_id, data in zip(r_v[1::2], r_v[2::2]):
            p = parse_kv(metric_map, data)
            if ("", str(probe_id)) not in setup_metrics:
                continue
            if "rtt" in p:
                # Latest RTT: 697 milliseconds
                rtt = p["rtt"].split()[0]
                try:
                    self.set_metric(
                        id=("SLA | UDP RTT", ("", probe_id)),
                        metric="SLA | UDP RTT",
                        value=float(rtt) * 1000,
                        multi=True,
                    )

                except ValueError:
                    pass
            if "sd_jitter" in p:
                # Source to Destination Jitter Min/Avg/Max: 0/8/106 milliseconds
                jitter = p["sd_jitter"].split()[0].split("/")[1]
                self.set_metric(
                    id=("SLA | JITTER", ("", probe_id)),
                    metric="SLA | JITTER",
                    value=float(jitter) * 1000,
                    multi=True,
                )

    @metrics(
        ["SLA | ICMP RTT"],
        has_capability="Cisco | IP | SLA | Probes",
        volatile=False,
        access="C",  # CLI version
    )
    def get_ip_sla_icmp_echo_metrics_cli(self, metrics):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        setup_metrics = {
            tuple(m.path): m.id
            for m in metrics
            if m.metric == "SLA | ICMP RTT" and m.sla_type == "icmp-echo"
        }
        if not setup_metrics:
            self.logger.info("No icmp-echo sla probes.")
            return
        v = self.cli("show ip sla statistics")
        metric_map = {"ipsla operation id": "name", "latest rtt": "rtt", "number of rtt": "num_rtt"}

        r_v = self.rx_ipsla_probe.split(v)
        if len(r_v) < 3:
            return

        for probe_id, data in zip(r_v[1::2], r_v[2::2]):
            p = parse_kv(metric_map, data)
            if ("", str(probe_id)) not in setup_metrics:
                continue
            if "rtt" in p:
                # Latest RTT: 697 milliseconds
                rtt = p["rtt"].split()[0]
                try:
                    self.set_metric(
                        id=setup_metrics[("", str(probe_id))],
                        metric="SLA | ICMP RTT",
                        path=("", probe_id),
                        value=float(rtt) * 1000,
                        multi=True,
                    )
                except ValueError:
                    pass

    @metrics(
        ["SLA | Jitter | Ingress", "SLA | Jitter | Egress", "SLA | Jitter | Rtt"],
        has_capability="Cisco | IP | SLA | Probes",
        volatile=False,
        access="S",  # CLI version
    )
    def get_ip_sla_udp_jitter_metrics_snmp(self, metrics):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        setup_metrics = {
            tuple(m.path): m.id
            for m in metrics
            if m.metric in {"SLA | Jitter | Ingress", "SLA | Jitter | Egress", "SLA | Jitter | Rtt"}
        }

        for sla_index, sla_rtt_sum, sla_egress, sla_ingress in self.snmp.get_tables(
            [
                "1.3.6.1.4.1.9.9.42.1.3.5.1.9",
                "1.3.6.1.4.1.9.9.42.1.3.5.1.63",
                "1.3.6.1.4.1.9.9.42.1.3.5.1.64",
            ],
            bulk=False,
        ):
            sla_probe_index, m_timestamp = sla_index.split(".")
            if ("", str(sla_probe_index)) not in setup_metrics:
                continue
            if sla_rtt_sum:
                self.set_metric(
                    id=setup_metrics[("", str(sla_probe_index))],
                    metric="SLA | Jitter | Rtt",
                    path=("", sla_probe_index),
                    value=float(sla_rtt_sum) * 1000.0,
                    multi=True,
                )
            if sla_egress:
                self.set_metric(
                    id=setup_metrics[("", str(sla_probe_index))],
                    metric="SLA | Jitter | Egress",
                    path=("", sla_probe_index),
                    value=float(sla_egress) * 1000.0,
                    multi=True,
                )
            if sla_ingress:
                self.set_metric(
                    id=setup_metrics[("", str(sla_probe_index))],
                    metric="SLA | Jitter | Ingress",
                    path=("", sla_probe_index),
                    value=float(sla_ingress) * 1000.0,
                    multi=True,
                )
