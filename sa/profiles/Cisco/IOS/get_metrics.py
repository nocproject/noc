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

SCALE_METRICS = {
    "SLA | OneWayLatency | Out | Max",
    "SLA | OneWayLatency | In | Max",
    "SLA | Jitter | Avg",
    "SLA | Jitter | Out | Avg",
    "SLA | Jitter | In | Avg",
    "SLA | RTT | Min",
    "SLA | RTT | Max",
}

SLA_ICMP_METRIC_MAP = {
    "SLA | RTT | Min": "CISCO-RTTMON-MIB::rttMonStatsCaptureCompletionTimeMin",
    "SLA | RTT | Max": "CISCO-RTTMON-MIB::rttMonStatsCaptureCompletionTimeMax",
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
                    labels = ifaces[item["ifindex"]] + [f'noc::traffic_class::{item["cmap_name"]}']
                    if "tos" in item:
                        labels.append(f'noc::tos::{item["tos"]}')
                    oids[mib[mc[0], item["pmap_index"], c]] = [
                        metric,
                        mc,
                        ifaces[item["ifindex"]],
                        labels,
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
            probe_status = {}
            for oid, oper_status in self.snmp.getnext(
                mib["CISCO-RTTMON-MIB::rttMonLatestRttOperSense"]
            ):
                _, name = oid.rsplit(".", 1)
                probe_status[name] = oper_status
                self.set_metric(
                    id=("SLA | Test | Status", [f"noc::sla::name::{name}"]),
                    metric="SLA | Test | Status",
                    value=float(oper_status),
                    ts=0,
                    labels=[f"noc::sla::name::{name}"],
                    multi=True,
                    type="gauge",
                    scale=1,
                )
            jitter_metrics = []
            icmp_metrics = {}
            for m in metrics:
                if m.metric not in SLA_METRICS_MAP:
                    continue
                name = next(
                    iter(
                        [
                            m.rsplit("::", 1)[-1]
                            for m in (m.labels or [])
                            if m.startswith("noc::sla::name::")
                        ]
                    ),
                    None,
                )
                if not name:
                    self.logger.warning("Unknown name for probe. Skipping")
                    continue
                if probe_status[name] != 1:
                    self.logger.debug("[%s] Test is not success. Skipping", name)
                    continue
                if m.sla_type == "icmp-echo" and m.metric in SLA_ICMP_METRIC_MAP:
                    icmp_metrics[(name, m.metric)] = m
                    continue
                jitter_metrics.append(m)
            if icmp_metrics:
                self.get_ip_sla_icmp_metrics_snmp(icmp_metrics)
            if jitter_metrics:
                self.get_ip_sla_udp_jitter_metrics_snmp(jitter_metrics)

    def get_ip_sla_icmp_metrics_snmp(self, metrics):
        scale = 1000
        ts = self.get_ts()
        for metric, m_oid in SLA_ICMP_METRIC_MAP.items():
            for oid, value in self.snmp.getnext(mib[m_oid]):
                _, name, timestamp, path, hop, dist = oid.rsplit(".", 5)
                if (name, metric) not in metrics:
                    continue
                m = metrics[(name, metric)]
                self.set_metric(
                    id=m.id,
                    metric=m.metric,
                    value=float(value),
                    ts=ts,
                    labels=m.labels,
                    multi=True,
                    type="gauge",
                    scale=scale if m.metric in SCALE_METRICS else 1,
                )

    def get_ip_sla_udp_jitter_metrics_snmp(self, metrics):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        #
        scale = 1000
        oids = {}
        for m in metrics:
            name = next(
                iter([m.rsplit("::", 1)[-1] for m in m.labels if m.startswith("noc::sla::name::")]),
                None,
            )
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
                scale=scale if m.metric in SCALE_METRICS else 1,
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
