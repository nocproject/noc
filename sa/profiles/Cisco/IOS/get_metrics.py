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
from noc.core.mib import mib


SLA_METRICS_MAP = {
    "SLA | Packets": "CISCO-RTTMON-MIB::rttMonLatestJitterOperNumOfRTT",
    "SLA | Packets | Loss | Out": "CISCO-RTTMON-MIB::rttMonLatestJitterOperPacketLossSD",
    "SLA | Packets | Loss | In": "CISCO-RTTMON-MIB::rttMonLatestJitterOperPacketLossDS",
    "SLA | Packets | Disordered": "CISCO-RTTMON-MIB::rttMonLatestJitterOperPacketOutOfSequence",
    # "SLA | Probes | Error": "CISCO-RTTMON-MIB::nqaJitterStatsErrors",
    "SLA | OneWayLatency | Out | Max": "CISCO-RTTMON-MIB::rttMonLatestJitterOperOWAvgSD",
    "SLA | OneWayLatency | In | Max": "CISCO-RTTMON-MIB::rttMonLatestJitterOperOWAvgDS",
    "SLA | Jitter | Avg": "CISCO-RTTMON-MIB::rttMonLatestJitterOperAvgJitter",
    "SLA | Jitter | Out | Avg": "CISCO-RTTMON-MIB::rttMonLatestJitterOperAvgSDJ",
    "SLA | Jitter | In | Avg": "CISCO-RTTMON-MIB::rttMonLatestJitterOperAvgDSJ",
    "SLA | Jitter | MOS": "CISCO-RTTMON-MIB::rttMonLatestJitterOperMOS",
    "SLA | Jitter | ICPIF": "CISCO-RTTMON-MIB::rttMonLatestJitterOperICPIF",
    "SLA | RTT | Min": "CISCO-RTTMON-MIB::rttMonLatestJitterOperRTTMin",
    "SLA | RTT | Max": "CISCO-RTTMON-MIB::rttMonLatestJitterOperRTTMax",
}


class Script(GetMetricsScript):
    name = "Cisco.IOS.get_metrics"
    always_prefer = "S"

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
            tuple(m.labels): m.id for m in metrics if m.metric in {"SLA | JITTER", "SLA | UDP RTT"}
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
            if (f"noc::sla::name::{probe_id}",) not in setup_metrics:
                continue
            if "rtt" in p:
                # Latest RTT: 697 milliseconds
                rtt = p["rtt"].split()[0]
                try:
                    self.set_metric(
                        id=("SLA | UDP RTT", (f"noc::sla::name::{probe_id}",)),
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
                    id=("SLA | JITTER", (f"noc::sla::name::{probe_id}",)),
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
            tuple(m.labels): m.id
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
            if (f"noc::sla::name::{probe_id}",) not in setup_metrics:
                continue
            if "rtt" in p:
                # Latest RTT: 697 milliseconds
                rtt = p["rtt"].split()[0]
                try:
                    self.set_metric(
                        id=setup_metrics[(f"noc::sla::name::{probe_id}",)],
                        metric="SLA | ICMP RTT",
                        labels=(f"noc::sla::name::{probe_id}",),
                        value=float(rtt) * 1000,
                        multi=True,
                    )
                except ValueError:
                    pass

    def get_cbqos_config_snmp(self):
        class_map = {}
        for oid, name in self.snmp.getnext(mib["CISCO-CLASS-BASED-QOS-MIB::cbQosCMName"]):
            class_map[oid.rsplit(".", 1)[-1]] = name
        policy_map = {}
        for oid, iftype, direction, ifindex in self.snmp.get_tables(
            [
                mib["CISCO-CLASS-BASED-QOS-MIB::cbQosIfType"],
                mib["CISCO-CLASS-BASED-QOS-MIB::cbQosPolicyDirection"],
                mib["CISCO-CLASS-BASED-QOS-MIB::cbQosIfIndex"],
            ],
            bulk=False,
        ):
            # direction 1 - input, 2 - output
            policy_map[oid.rsplit(".", 1)[-1]] = {
                "iftype": iftype,
                "direction": {1: "In", 2: "Out"}[direction],
                "ifindex": ifindex,
            }
        config_cmap = {}
        for entry_index, config_index, object_type, parent in self.snmp.get_tables(
            [
                mib["CISCO-CLASS-BASED-QOS-MIB::cbQosConfigIndex"],
                mib["CISCO-CLASS-BASED-QOS-MIB::cbQosObjectsType"],
                mib["CISCO-CLASS-BASED-QOS-MIB::cbQosParentObjectsIndex"],
            ],
            bulk=False,
        ):
            if object_type != 2:
                # class-map only
                continue
            policy_index, object_index = entry_index.split(".")
            config_cmap[object_index] = {
                "pmap_index": policy_index,
                "type": object_type,
                "cmap_name": class_map[str(config_index)],
                "cmap_index": config_index,
            }
            config_cmap[object_index].update(policy_map[policy_index])
        return config_cmap

    CBQOS_OIDS_MAP = {
        # oid, type, scale
        "In": {
            "Interface | CBQOS | Drops | In | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMDropByte",
                "delta",
                1,
            ),
            "Interface | CBQOS | Octets | In | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMPostPolicyByte",
                "delta",
                1,
            ),
        },
        "Out": {
            "Interface | CBQOS | Drops | Out | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMDropByte",
                "delta",
                1,
            ),
            "Interface | CBQOS | Octets | Out | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMPostPolicyByte",
                "delta",
                1,
            ),
        },
    }

    @metrics(
        [
            "Interface | CBQOS | Drops | In | Delta",
            "Interface | CBQOS | Drops | Out | Delta",
            "Interface | CBQOS | Octets | In | Delta",
            "Interface | CBQOS | Octets | Out | Delta",
        ],
        volatile=False,
        access="S",  # CLI version
    )
    def get_interface_cbqos_metrics_snmp(self, metrics):
        print(metrics)
        ifaces = {m.ifindex: m.labels for m in metrics if m.ifindex}
        config = self.get_cbqos_config_snmp()
        oids = {}
        for c, item in config.items():
            if item["ifindex"] in ifaces:
                for metric, mc in self.CBQOS_OIDS_MAP[item["direction"]].items():
                    oids[mib[mc[0], item["pmap_index"], c]] = [
                        metric,
                        mc,
                        ifaces[item["ifindex"]],
                        ifaces[item["ifindex"]] + [f'noc::traffic_class::{item["cmap_name"]}'],
                    ]
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in results:
            # if not results[r]:
            #     continue
            metric, mc, mlabesl, labels = oids[r]
            _, mtype, scale = mc
            self.set_metric(
                id=(metric, mlabesl),
                metric=metric,
                value=float(results[r]),
                ts=ts,
                labels=labels,
                multi=True,
                type=mtype,
                scale=scale,
            )
        # print(r)
        # "noc::traffic_class::*", "noc::interface::*"

    def collect_profile_metrics(self, metrics):
        # SLA Metrics
        if self.has_capability("Cisco | IP | SLA | Probes"):
            self.get_ip_sla_udp_jitter_metrics_snmp(
                [m for m in metrics if m.metric in SLA_METRICS_MAP]
            )

    def get_ip_sla_udp_jitter_metrics_snmp(self, metrics):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        oids = {}
        # stat_index = 250
        stat_index = {}
        for oid, r in self.snmp.getnext(mib["NQA-MIB::nqaJitterStatsCompletions"], only_first=True):
            key = ".".join(oid.split(".")[14:-1])
            stat_index[key] = oid.rsplit(".", 1)[-1]
        for m in metrics:
            if m.metric not in SLA_METRICS_MAP:
                continue
            if len(m.labels) < 2:
                continue
            _, name = m.labels[0].rsplit("::", 1)
            _, group = m.labels[1].rsplit("::", 1)
            key = f'{len(group)}.{".".join(str(ord(s)) for s in group)}.{len(name)}.{".".join(str(ord(s)) for s in name)}'
            oid = mib[
                SLA_METRICS_MAP[m.metric],
                name,
            ]
            oids[oid] = m
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in results:
            if results[r] is None:
                continue
            m = oids[r]
            self.set_metric(
                id=m.id,
                metric=m.metric,
                value=float(results[r]),
                ts=ts,
                labels=m.labels,
                multi=True,
                type="gauge",
                scale=1,
            )
