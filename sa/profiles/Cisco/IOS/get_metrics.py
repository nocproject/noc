# ---------------------------------------------------------------------
# Cisco.IOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import List, Dict, Tuple, Union

# NOC modules
from noc.sa.profiles.Generic.get_metrics import (
    Script as GetMetricsScript,
    metrics,
    ProfileMetricConfig,
    MetricConfig,
)
from noc.core.models.cfgmetrics import MetricCollectorConfig
from noc.core.mib import mib
from noc.core.text import parse_kv


SLA_ICMP_METRIC_MAP = {
    "SLA | RTT | Min": "CISCO-RTTMON-MIB::rttMonStatsCaptureCompletionTimeMin",
    "SLA | RTT | Max": "CISCO-RTTMON-MIB::rttMonStatsCaptureCompletionTimeMax",
}


class Script(GetMetricsScript):
    name = "Cisco.IOS.get_metrics"
    always_prefer = "S"

    SLA_METRICS_CONFIG = {
        "SLA | Packets": ProfileMetricConfig(
            metric="SLA | Packets",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperNumOfRTT",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Loss | Out": ProfileMetricConfig(
            metric="SLA | Packets | Loss | Out",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperPacketLossSD",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Loss | In": ProfileMetricConfig(
            metric="SLA | Packets | Loss | In",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperPacketLossDS",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Disordered": ProfileMetricConfig(
            metric="SLA | Packets | Loss | In",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperPacketOutOfSequence",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        # "SLA | Probes | Error": "CISCO-RTTMON-MIB::nqaJitterStatsErrors",
        "SLA | OneWayLatency | Out | Max": ProfileMetricConfig(
            metric="SLA | OneWayLatency | Out | Max",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperOWAvgSD",
            sla_types=["udp-jitter"],
            scale=1,
            units="u,s",
        ),
        "SLA | OneWayLatency | In | Max": ProfileMetricConfig(
            metric="SLA | OneWayLatency | In | Max",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperOWAvgDS",
            sla_types=["udp-jitter"],
            scale=1,
            units="u,s",
        ),
        "SLA | Jitter | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | Avg",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperAvgJitter",
            sla_types=["udp-jitter"],
            scale=1,
            units="u,s",
        ),
        "SLA | Jitter | Out | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | Out | Avg",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperAvgSDJ",
            sla_types=["udp-jitter"],
            scale=1,
            units="u,s",
        ),
        "SLA | Jitter | In | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | In | Avg",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperAvgDSJ",
            sla_types=["udp-jitter"],
            scale=1,
            units="u,s",
        ),
        "SLA | Jitter | MOS": ProfileMetricConfig(
            metric="SLA | Jitter | MOS",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperMOS",
            sla_types=["udp-jitter"],
            scale=1,
            units="u,s",
        ),
        "SLA | Jitter | ICPIF": ProfileMetricConfig(
            metric="SLA | Jitter | ICPIF",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperICPIF",
            sla_types=["udp-jitter"],
            scale=1,
            units="u,s",
        ),
        "SLA | RTT | Min": ProfileMetricConfig(
            metric="SLA | RTT | Min",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperRTTMin",
            sla_types=["udp-jitter", "icmp-echo"],
            scale=1,
            units="u,s",
        ),
        "SLA | RTT | Max": ProfileMetricConfig(
            metric="SLA | RTT | Max",
            oid="CISCO-RTTMON-MIB::rttMonLatestJitterOperRTTMax",
            sla_types=["udp-jitter", "icmp-echo"],
            scale=1,
            units="u,s",
        ),
    }

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
                        units="micro,s",
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
                    units="micro,s",
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
                        units="micro,s",
                    )
                except ValueError:
                    pass

    def get_cbqos_config_snmp(self) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Return config for build metric index
        :return:
        """
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
        class_tos_map = {}
        # DSCP collect
        for oid, dscp in self.snmp.getnext(
            mib["CISCO-CLASS-BASED-QOS-MIB::cbQosSetCfgIpDSCPValue"]
        ):
            _, index = oid.rsplit(".", 1)
            class_tos_map[int(index)] = dscp
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
            if config_index in class_tos_map:
                config_cmap[object_index]["tos"] = class_tos_map[config_index]
            config_cmap[object_index].update(policy_map[policy_index])
        return config_cmap

    CBQOS_OIDS_MAP: Dict[str, Dict[str, Tuple[str, str, int, str]]] = {
        # oid, type, scale
        "In": {
            "Interface | CBQOS | Drops | In | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMDropByte",
                "delta",
                1,
                "pkt",
            ),
            "Interface | CBQOS | Octets | In | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMPostPolicyByte",
                "delta",
                1,
                "byte",
            ),
        },
        "Out": {
            "Interface | CBQOS | Drops | Out | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMDropByte",
                "delta",
                1,
                "pkt",
            ),
            "Interface | CBQOS | Octets | Out | Delta": (
                "CISCO-CLASS-BASED-QOS-MIB::cbQosCMPostPolicyByte",
                "delta",
                1,
                "byte",
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
    def get_interface_cbqos_metrics_snmp(self, metrics: List[MetricConfig]):
        ifaces = {m.ifindex: m for m in metrics if m.ifindex}
        config = self.get_cbqos_config_snmp()
        oids: Dict[str, Tuple[str, Tuple[str, str, int, str], MetricConfig, List[str]]] = {}
        for c, item in config.items():
            if item["ifindex"] in ifaces:
                for metric, mc in self.CBQOS_OIDS_MAP[item["direction"]].items():
                    labels = ifaces[item["ifindex"]].labels + [
                        f'noc::traffic_class::{item["cmap_name"]}'
                    ]
                    if "tos" in item:
                        labels.append(f'noc::tos::{item["tos"]}')
                    oids[mib[mc[0], item["pmap_index"], c]] = (
                        metric,
                        mc,
                        ifaces[item["ifindex"]],
                        labels,
                    )
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in results:
            # if not results[r]:
            #     continue
            metric, mc, s_cfg, labels = oids[r]
            _, mtype, scale, units = mc
            self.set_metric(
                id=(metric, s_cfg.labels),
                metric=metric,
                value=float(results[r]),
                ts=ts,
                labels=labels,
                multi=True,
                type=mtype,
                scale=scale,
                units=units,
                service=s_cfg.service,
            )

        # print(r)
        # "noc::traffic_class::*", "noc::interface::*"

    def collect_sla_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect SLA metrics for Cisco
        :param metrics:
        :return:
        """
        # SLA Metrics
        if not self.has_capability("Cisco | IP | SLA | Probes"):
            return
        probe_status = {}
        # Collect probe oper status
        for oid, oper_status in self.snmp.getnext(
            mib["CISCO-RTTMON-MIB::rttMonLatestRttOperSense"]
        ):
            _, name = oid.rsplit(".", 1)
            probe_status[name] = oper_status
        # Create config for collect. Split Jitter and ICMP probe, that used different  OID
        jitter_probes, icmp_probes = [], {}
        for probe in metrics:
            hints = probe.get_hints()
            name = hints.get("sla_name")
            if not name or name not in probe_status:
                self.logger.warning("Unknown name for probe. Skipping")
                continue
            # Set probe status
            self.set_metric(
                id=probe.sla_probe,
                metric="SLA | Test | Status",
                value=float(probe_status[name]),
                ts=self.get_ts(),
                labels=[f"noc::sla::name::{name}"],
                sensor=probe.sla_probe,
                multi=True,
                type="gauge",
                scale=1,
            )
            if probe_status[name] != 1:
                self.logger.debug("[%s] Test is not success. Skipping", name)
                continue
            requested_metrics = set(probe.metrics)
            if hints["sla_type"] == "icmp-echo":
                for metric in probe.metrics:
                    if metric not in SLA_ICMP_METRIC_MAP:
                        continue
                    icmp_probes[(name, metric)] = probe
                continue
            if not requested_metrics.intersection(set(self.SLA_METRICS_CONFIG)):
                continue
            jitter_probes.append(probe)
        if icmp_probes:
            self.get_ip_sla_icmp_metrics_snmp(icmp_probes)
        if jitter_probes:
            self.get_ip_sla_udp_jitter_metrics_snmp(jitter_probes)

    def get_ip_sla_icmp_metrics_snmp(self, metrics: Dict[Tuple[str, str], MetricCollectorConfig]):
        ts = self.get_ts()
        for metric, m_oid in SLA_ICMP_METRIC_MAP.items():
            for oid, value in self.snmp.getnext(mib[m_oid]):
                _, name, timestamp, path, hop, dist = oid.rsplit(".", 5)
                if (name, metric) not in metrics:
                    continue
                probe = metrics[(name, metric)]
                self.set_metric(
                    id=(metric, [str(probe.sla_probe)]),
                    metric=metric,
                    value=float(value),
                    ts=ts,
                    labels=probe.labels,
                    sla_probe=probe.sla_probe,
                    multi=True,
                    type="gauge",
                    scale=1000,
                    units="s",  # Second
                )

    def get_ip_sla_udp_jitter_metrics_snmp(self, metrics: List[MetricCollectorConfig]):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        #
        oids = {}
        for probe in metrics:
            hints = probe.get_hints()
            name = hints["sla_name"]
            for m in probe.metrics:
                if m not in self.SLA_METRICS_CONFIG:
                    continue
                mc = self.SLA_METRICS_CONFIG[m]
                oid = mib[mc.oid, name]
                oids[oid] = (probe, mc)
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in results:
            if results[r] is None:
                continue
            probe, mc = oids[r]
            self.set_metric(
                id=probe.sla_probe,
                sla_probe=probe.sla_probe,
                metric=mc.metric,
                value=float(results[r]),
                ts=ts,
                labels=probe.labels,
                multi=True,
                type="gauge",
                scale=mc.scale,
                units=mc.units,
            )
        #

    @metrics(["Telephony | Active DS0s"], volatile=False, access="S")
    def get_active_ds0s(self, metrics):
        """
        Returns active DS0 channels
        :return:
        """
        # CISCO-POP-MGMT-MIB::cpmDS1ActiveDS0s
        ds0_oid = "1.3.6.1.4.1.9.10.19.1.1.9.1.3"
        for oid, v in self.snmp.getnext(ds0_oid, bulk=False):
            oid2 = oid.split(ds0_oid + ".")
            (slot, port) = oid2[1].split(".")
            self.set_metric(
                id=("Telephony | Active DS0s", None),
                labels=[f"noc::slot::{slot}", f"noc::interface::{port}"],
                value=int(v),
                multi=True,
            )
