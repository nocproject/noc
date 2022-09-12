# ---------------------------------------------------------------------
# Huawei.VRP.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List

# NOC modules
from noc.core.models.cfgmetrics import MetricCollectorConfig
from noc.sa.profiles.Generic.get_metrics import (
    Script as GetMetricsScript,
    metrics,
    ProfileMetricConfig,
)
from noc.core.models.cfgmetrics import MetricCollectorConfigz
from .oidrules.slot import SlotRule
from .oidrules.sslot import SSlotRule
from noc.core.mib import mib


SLA_ICMP_METRIC_MAP = {
    "SLA | Packets | Loss | Ratio": "NQA-MIB::nqaResultsLostPacketRatio",
    "SLA | RTT | Max": "NQA-MIB::nqaResultsRttAvg",
}


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

    OID_RULES = [SlotRule, SSlotRule]
    SLA_METRICS_CONFIG = {
        "SLA | Packets": ProfileMetricConfig(
            metric="SLA | Packets",
            oid="NQA-MIB::nqaJitterStatsSentProbes",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Loss | Ratio": ProfileMetricConfig(
            metric="SLA | Packets | Loss | Ratio",
            oid="NQA-MIB::nqaJitterCollectStatsPacketLossRatio",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Loss | Out": ProfileMetricConfig(
            metric="SLA | Packets | Loss | Out",
            oid="NQA-MIB::nqaJitterStatsPacketLossSD",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Loss | In": ProfileMetricConfig(
            metric="SLA | Packets | Loss | In",
            oid="NQA-MIB::nqaJitterStatsPacketLossDS",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Disordered": ProfileMetricConfig(
            metric="SLA | Packets | Disordered",
            oid="NQA-MIB::nqaJitterStatsPktDisorderNum",
            sla_types=["udp-jitter"],
            scale=1,
            units="pkt",
        ),
        "SLA | Probes | Error": ProfileMetricConfig(
            metric="SLA | Probes | Error",
            oid="NQA-MIB::nqaJitterStatsErrors",
            sla_types=["udp-jitter"],
            scale=1,
            units="1",
        ),
        # Latency
        "SLA | OneWayLatency | Out | Max": ProfileMetricConfig(
            metric="SLA | OneWayLatency | Out | Max",
            oid="NQA-MIB::nqaJitterStatsMaxDelaySD",
            sla_types=["udp-jitter"],
            scale=1000,
            units="micro,s",
        ),
        "SLA | OneWayLatency | In | Max": ProfileMetricConfig(
            metric="SLA | OneWayLatency | In | Max",
            oid="NQA-MIB::nqaJitterStatsMaxDelayDS",
            sla_types=["udp-jitter"],
            scale=1000,
            units="micro,s",
        ),
        # Jitter
        "SLA | Jitter | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | Avg",
            oid="NQA-MIB::nqaJitterStatsAvgJitter",
            sla_types=["udp-jitter"],
            scale=1000,
            units="micro,s",
        ),
        "SLA | Jitter | Out | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | Out | Avg",
            oid="NQA-MIB::nqaJitterStatsAvgJitterSD",
            sla_types=["udp-jitter"],
            scale=1000,
            units="micro,s",
        ),
        "SLA | Jitter | In | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | In | Avg",
            oid="NQA-MIB::nqaJitterStatsAvgJitterDS",
            sla_types=["udp-jitter"],
            scale=1000,
            units="micro,s",
        ),
        "SLA | Jitter | MOS": ProfileMetricConfig(
            metric="SLA | Jitter | MOS",
            oid="NQA-MIB::nqaJitterStatsOperOfMos",
            sla_types=["udp-jitter"],
            scale=1,
            units="micro,s",
        ),
        "SLA | Jitter | ICPIF": ProfileMetricConfig(
            metric="SLA | Jitter | ICPIF",
            oid="NQA-MIB::nqaJitterStatsOperOfIcpif",
            sla_types=["udp-jitter"],
            scale=1,
            units="micro,s",
        ),
        "SLA | RTT | Min": ProfileMetricConfig(
            metric="SLA | RTT | Min",
            oid="NQA-MIB::nqaJitterStatsRTTMin",
            sla_types=["udp-jitter", "icmp-echo"],
            scale=1000,
            units="micro,s",
        ),
        "SLA | RTT | Max": ProfileMetricConfig(
            metric="SLA | RTT | Max",
            oid="NQA-MIB::nqaJitterStatsRTTMax",
            sla_types=["udp-jitter", "icmp-echo"],
            scale=1000,
            units="micro,s",
        ),
    }

    @metrics(
        ["Interface | Status | Duplex"],
        has_capability="DB | Interfaces",
        matcher="is_cx200X",
        volatile=False,
        access="S",
    )
    def get_duplex_interface_metrics(self, metrics):
        if_map = {
            m.ifindex: m.labels
            for m in metrics
            if m.ifindex and m.metric == "Interface | Status | Duplex"
        }
        for oid, duplex in self.snmp.getnext(mib["EtherLike-MIB::dot3StatsDuplexStatus"]):
            _, ifindex = oid.rsplit(".", 1)
            if int(ifindex) not in if_map:
                continue
            self.set_metric(id=("Interface | Status | Duplex", if_map[int(ifindex)]), value=duplex)

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",  # not CLI version
    )
    def get_subscribers_metrics(self, metrics):
        if "Slot | Member Ids" in self.capabilities:
            hwSlotIndex = self.capabilities["Slot | Member Ids"].split(" | ")
            for si in hwSlotIndex:
                for mi in [0, 1]:
                    v = self.snmp.get(f"1.3.6.1.4.1.2011.5.2.1.33.1.8.{si}.{mi}")
                    if v:
                        self.set_metric(
                            id=("Subscribers | Summary", None),
                            labels=("noc::chassis::0", f"noc::slot::{si}", f"noc::module::{mi}"),
                            value=int(v),
                            multi=True,
                        )
        v = self.snmp.get("1.3.6.1.4.1.2011.5.2.1.14.1.2.0")
        if v:
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=[],
                value=int(v),
                multi=True,
            )

    @metrics(
        [
            "Interface | CBQOS | Drops | In | Delta",
            "Interface | CBQOS | Drops | Out | Delta",
            "Interface | CBQOS | Octets | In | Delta",
            "Interface | CBQOS | Octets | Out | Delta",
            "Interface | CBQOS | Packets | In | Delta",
            "Interface | CBQOS | Packets | Out | Delta",
        ],
        volatile=False,
        access="S",  # CLI version
    )
    def get_interface_cbqos_metrics_snmp(self, metrics):
        """
        Use available SNMP Table for collecting value
        :param metrics:
        :return:
        """
        if self.has_capability("Huawei | OID | hwCBQoSPolicyStatisticsClassifierTable"):
            self.get_interface_cbqos_metrics_policy_snmp(metrics)
        elif self.has_capability("Huawei | OID | hwCBQoSClassifierStatisticsTable"):
            self.get_interface_cbqos_metrics_classifier_snmp(metrics)

    def get_interface_cbqos_metrics_classifier_snmp(self, metrics):
        self.logger.debug("Use hwCBQoSClassifierStatisticsTable for collected metrics")
        ifaces = {m.ifindex: m.labels for m in metrics if m.ifindex}
        direction_map = {1: "In", 2: "Out"}
        class_map = {}
        for oid, name in self.snmp.getnext(mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierName"]):
            class_map[oid.rsplit(".", 1)[-1]] = name
        for index, packets, bytes, discards in self.snmp.get_tables(
            [
                mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierMatchedPackets"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierMatchedBytes"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierMatchedDropPackets"],
            ]
        ):
            ifindex, direction, ifvlanid1, ifvlanid2, classifier = index.split(".")
            if ifindex not in ifaces:
                continue
            ts = self.get_ts()
            for metric, value in [
                (f"Interface | CBQOS | Drops | {direction_map[direction]} | Delta", discards),
                (f"Interface | CBQOS | Octets | {direction_map[direction]} | Delta", bytes),
                # (f"Interface | CBQOS | Octets | {direction_map[direction]}", bytes),
                (f"Interface | CBQOS | Packets | {direction_map[direction]} | Delta", packets),
                # (f"Interface | CBQOS | Packets | {direction_map[direction]}", packets),
            ]:
                scale = 1
                self.set_metric(
                    id=(metric, ifaces[ifindex]),
                    metric=metric,
                    value=float(value),
                    ts=ts,
                    labels=ifaces[ifindex] + [f"noc::traffic_class::{class_map[classifier]}"],
                    multi=True,
                    type="delta" if metric.endswith("Delta") else "gauge",
                    scale=scale,
                    units="pkt" if "Octets" in metric else "byte",
                )

    def get_interface_cbqos_metrics_policy_snmp(self, metrics):
        self.logger.debug("Use hwCBQoSPolicyStatisticsClassifierTable for collected metrics")
        ifaces = {m.ifindex: m.labels for m in metrics if m.ifindex}
        direction_map = {"1": "In", "2": "Out"}
        class_tos_map = self.get_classifier_tos()
        self.logger.debug("Class TOS map: %s", class_tos_map)
        for index, packets, bytes, discards in self.snmp.get_tables(
            [
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyStatClassifierMatchedPassPackets"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyStatClassifierMatchedPassBytes"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyStatClassifierMatchedDropPackets"],
            ]
        ):
            ifindex, ifvlanid1, direction, classifier = index.split(".", 3)
            ifindex = int(ifindex)
            if not ifindex or ifindex not in ifaces:
                self.logger.info("Interface Vlan %s not collected", ifvlanid1)
                # Interface vlan
                continue
            traffic_class = "".join(chr(int(c)) for c in classifier.split(".")[1:])
            ts = self.get_ts()
            for metric, value in [
                (f"Interface | CBQOS | Drops | {direction_map[direction]} | Delta", discards),
                (f"Interface | CBQOS | Octets | {direction_map[direction]} | Delta", bytes),
                # (f"Interface | CBQOS | Load | {direction_map[direction]}", bytes),
                (f"Interface | CBQOS | Packets | {direction_map[direction]} | Delta", packets),
                # (f"Interface | CBQOS | Packets | {direction_map[direction]}", packets),
            ]:
                mtype, scale = "gauge", 1
                if metric.endswith("Delta"):
                    mtype = "delta"
                if traffic_class in class_tos_map:
                    labels = [
                        f"noc::traffic_class::{traffic_class}",
                        f"noc::tos::{class_tos_map[traffic_class]}",
                    ]
                else:
                    labels = [f"noc::traffic_class::{traffic_class}"]
                self.set_metric(
                    id=(metric, ifaces[ifindex]),
                    metric=metric,
                    value=float(value),
                    ts=ts,
                    labels=ifaces[ifindex] + labels,
                    multi=True,
                    type=mtype,
                    scale=scale,
                    units="pkt" if "Octets" in metric else "byte",
                )

    def collect_sla_metrics(self, metrics: List[MetricCollectorConfig]):
        # SLA Metrics
        if not self.has_capability("Huawei | NQA | Probes"):
            return
        jitter_metrics = []
        icmp_metrics = []
        for probe in metrics:
            # if m.metric not in self.SLA_METRICS_CONFIG:
            #    continue
            hints = probe.get_hints()
            if hints["sla_type"] == "icmp-echo":
                icmp_metrics.append(probe)
            else:
                jitter_metrics.append(probe)
        if icmp_metrics:
            self.get_ip_sla_udp_jitter_metrics_snmp(icmp_metrics, metric_map=SLA_ICMP_METRIC_MAP)
        if jitter_metrics:
            self.get_ip_sla_udp_jitter_metrics_snmp(
                jitter_metrics,
                metric_map=self.SLA_METRICS_CONFIG,
                status_oid="NQA-MIB::nqaJitterStatsCompletions",
            )

    def get_ip_sla_udp_jitter_metrics_snmp(
        self,
        metrics: List[MetricCollectorConfig],
        metric_map,
        status_oid="NQA-MIB::nqaResultsCompletions",
    ):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        oids = {}
        # stat_index = 250
        stat_index, probe_status = {}, {}
        scale = 1000
        ts = self.get_ts()
        for oid, value in self.snmp.getnext(mib[status_oid]):
            if status_oid == "NQA-MIB::nqaResultsCompletions":
                *key, resindex, addindex = oid.split(".")
            else:
                *key, resindex = oid.split(".")
            key = key[14:]
            fi = int(key[0])
            owner, test_name = key[1 : fi + 1], key[fi + 2 :]
            if ".".join(key) in stat_index:
                continue
            stat_index[".".join(key)] = resindex
            probe_status[".".join(key)] = value
        for probe in metrics:
            hints = probe.get_hints()
            name = hints["sla_name"]
            group = hints["group"]
            if not name or not group:
                continue
            key = f'{len(group)}.{".".join(str(ord(s)) for s in group)}.{len(name)}.{".".join(str(ord(s)) for s in name)}'
            if key not in stat_index:
                continue
            for m in probe.metrics:
                mc = self.SLA_METRICS_CONFIG[m]
                if status_oid == "NQA-MIB::nqaResultsCompletions":
                    oid = mib[mc.oid, key, stat_index[key], 1]
                else:
                    oid = mib[mc.oid, key, stat_index[key]]
                oids[oid] = (probe, mc)
            self.set_metric(
                id=probe.sla_probe,
                metric="SLA | Test | Status",
                sla_probe=probe.sla_probe,
                value=float(probe_status[key]),
                ts=ts,
                labels=probe.labels,
                multi=True,
                type="gauge",
                scale=1,
            )
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
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

    def get_classifier_tos(self):
        r = {}  # classifier name -> tos map
        behavior_tos = {}
        for index, value in self.snmp.getnext(mib["HUAWEI-CBQOS-MIB::hwCBQoSRemarkValue"]):
            if not index.endswith("2"):
                continue
            _, b_id, b_type = index.rsplit(".", 2)
            behavior_tos[int(b_id)] = value

        for index, classifier, behavior_index in self.snmp.get_tables(
            [
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyClassClassifierName"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyClassBehaviorIndex"],
            ]
        ):
            if behavior_index not in behavior_tos:
                continue
            r[classifier] = behavior_tos[behavior_index]
        return r

    # @metrics(
    #     ["Interface | Errors | CRC", "Interface | Errors | Frame"],
    #     has_capability="DB | Interfaces",
    #     volatile=False,
    #     access="C",  # CLI version
    # )
    # def get_vrp_interface_metrics(self, metrics):
    #     v = self.cli("display interface")
    #     ifdata = self.profile.parse_ifaces(v)
    #     for iface, data in ifdata.items():
    #         iface = self.profile.convert_interface_name(iface)
    #         ipath = ["", "", "", iface]
    #         if "CRC" in data:
    #             self.set_metric(id=("Interface | Errors | CRC", ipath), value=int(data["CRC"]))
    #         if "Frames" in data:
    #             self.set_metric(id=("Interface | Errors | Frame", ipath), value=int(data["Frames"]))
