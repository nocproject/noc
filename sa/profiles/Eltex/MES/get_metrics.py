# ----------------------------------------------------------------------
# Eltex.MES.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import List

# NOC Modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics, MetricConfig


class Script(GetMetricsScript):
    name = "Eltex.MES.get_metrics"

    QOS_OIDS_MAP = {
        # oid, type, scale
        "Interface | QOS | Discards | Out | Delta": (5, "delta", 1, "pkt"),
        "Interface | QOS | Octets | Out": (6, "counter", 8, "byte"),
        "Interface | QOS | Packets | Out": (7, "counter", 1, "pkt"),
    }

    BASE_OID = "1.3.6.1.4.1.35265.1.23.1.8.1.2.1.1.1."

    def get_interface_qos(self, metrics: List["MetricConfig"]):
        oids = {}
        for mc in metrics:
            if not mc.ifindex:
                continue
            for q in range(1, 8):
                oids[
                    f"1.3.6.1.4.1.35265.1.23.1.8.1.2.1.1.1.{self.QOS_OIDS_MAP[mc.metric][0]}.{mc.ifindex}.{q}.0"
                ] = (mc, [*list(mc.labels), f"noc::queue::{q!s}", "noc::traffic_class::0"])
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in results:
            if not results[r]:
                continue
            mc, labels = oids[r]
            _, mtype, scale, units = self.QOS_OIDS_MAP[mc.metric]
            self.set_metric(
                id=(mc.metric, mc.labels),
                metric=mc.metric,
                value=float(results[r]),
                ts=ts,
                labels=labels,
                multi=True,
                type=mtype,
                scale=scale,
                units=units,
            )

    @metrics(
        ["Interface | QOS | Discards | Out | Delta"],
        has_capability="Metrics | QOS | Statistics",
        volatile=False,
        access="S",
    )
    def get_interface_qos_discards(self, metrics: List["MetricConfig"]):
        self.get_interface_qos(metrics)

    @metrics(
        ["Interface | QOS | Octets | Out"],
        has_capability="Metrics | QOS | Statistics",
        volatile=False,
        access="S",
    )
    def get_interface_qos_octets(self, metrics: List["MetricConfig"]):
        self.get_interface_qos(metrics)

    @metrics(
        ["Interface | QOS | Packets | Out"],
        has_capability="Metrics | QOS | Statistics",
        volatile=False,
        access="S",
    )
    def get_interface_qos_packets(self, metrics: List["MetricConfig"]):
        self.get_interface_qos(metrics)
