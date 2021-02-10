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
        "Interface | QOS | Discards | Out | Delta": (5, "delta", 1),
        "Interface | QOS | Octets | Out": (6, "counter", 8),
        "Interface | QOS | Packets | Out": (7, "counter", 1),
    }

    BASE_OID = "1.3.6.1.4.1.35265.1.23.1.8.1.2.1.1.1."

    @metrics(
        [
            "Interface | QOS | Discards | Out | Delta",
            "Interface | QOS | Octets | Out",
            "Interface | QOS | Packets | Out",
        ],
        has_capability="Metrics | QOS | Statistics",
        volatile=True,
        access="S",
    )
    def get_interface_qos_discards(self, metrics: List["MetricConfig"]):
        oids = {}
        for mc in metrics:
            if not mc.ifindex:
                continue
            for q in range(1, 8):
                oids[
                    f"1.3.6.1.4.1.35265.1.23.1.8.1.2.1.1.1.{self.QOS_OIDS_MAP[mc.metric][0]}.{mc.ifindex}.{q}.0"
                ] = (mc, list(mc.path) + [str(q), "0"])
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in results:
            if not results[r]:
                continue
            mc, path = oids[r]
            _, mtype, scale = self.QOS_OIDS_MAP[mc.metric]
            self.set_metric(
                id=(mc.metric, mc.path),
                metric=mc.metric,
                value=float(results[r]),
                ts=ts,
                path=path,
                multi=True,
                type=mtype,
                scale=scale,
            )
