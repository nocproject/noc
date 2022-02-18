# ---------------------------------------------------------------------
# Juniper.JUNOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
import enum

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule
from noc.core.mib import mib
from noc.core.script.metrics import scale


class RPMMeasurement(enum.Enum):
    roundTripTime = 1
    posRttJitter = 2
    negRttJitter = 3
    egress = 4
    posEgressJitter = 5
    negEgressJitter = 6
    ingress = 7
    posIngressJitter = 8
    negIngressJitter = 9


class RPMResultCollection(enum.Enum):
    currentTest = (1,)
    lastCompletedTest = 2
    movingAverage = 3
    allTests = 4


SLA_METRICS_MAP = {
    "SLA | Packets": "JUNIPER-RPM-MIB::jnxRpmResSumSent",
    "SLA | Packets | Loss | Ratio": "JUNIPER-RPM-MIB::jnxRpmResSumPercentLost",
    # "SLA | Packets | Loss | In": "JUNIPER-RPM-MIB::jnxRpmResSumReceived",
    "SLA | Jitter | Avg": ("JUNIPER-RPM-MIB::jnxRpmResCalcAverage", 4),
    "SLA | Jitter | Out | Avg": (
        "JUNIPER-RPM-MIB::jnxRpmResCalcAverage",
        RPMMeasurement.egress.value,
    ),
    "SLA | Jitter | In | Avg": (
        "JUNIPER-RPM-MIB::jnxRpmResCalcAverage",
        RPMMeasurement.ingress.value,
    ),
    "SLA | RTT | Min": ("JUNIPER-RPM-MIB::jnxRpmResCalcMin", RPMMeasurement.roundTripTime.value),
    "SLA | RTT | Max": ("JUNIPER-RPM-MIB::jnxRpmResCalcMax", RPMMeasurement.roundTripTime.value),
}


class Script(GetMetricsScript):
    name = "Juniper.JUNOS.get_metrics"
    OID_RULES = [SlotRule]

    @metrics(
        ["Subscribers | Summary"],
        has_capability="Metrics | Subscribers",
        volatile=False,
        access="S",  # not CLI version
    )
    def get_subscribers_metrics(self, metrics):
        if self.is_gte_16:
            for oid, v in self.snmp.getnext("1.3.6.1.4.1.2636.3.64.1.1.1.5.1.3", bulk=False):
                oid2 = oid.split("1.3.6.1.4.1.2636.3.64.1.1.1.5.1.3.")
                interf = oid2[1].split(".")
                del interf[0]
                port = ""
                for x in interf:
                    port += chr(int(x))
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    labels=("noc::chassis::0", f"noc::interface::{str(port)}"),
                    value=int(v),
                    multi=True,
                )
        metric = self.snmp.get("1.3.6.1.4.1.2636.3.64.1.1.1.2.0")
        if metric is not None:  # May be `None`. Bug in some JUNOS versions
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=("noc::chassis::0",),
                value=int(metric),
                multi=True,
            )

    @metrics(
        [
            "Interface | CBQOS | Drops | Out | Delta",
            "Interface | CBQOS | Octets | Out",
            "Interface | CBQOS | Octets | Out | Delta",
            "Interface | CBQOS | Packets | Out",
            "Interface | CBQOS | Packets | Out | Delta",
        ],
        volatile=False,
        has_capability="Juniper | OID | jnxCosIfqStatsTable",
        access="S",  # CLI version
    )
    def get_interface_cbqos_metrics_snmp(self, metrics):
        ifaces = {str(m.ifindex): m.labels for m in metrics if m.ifindex}
        for ifindex in ifaces:
            for index, packets, octets, discards in self.snmp.get_tables(
                [
                    mib["JUNIPER-COS-MIB::jnxCosIfqTxedPkts", ifindex],
                    mib["JUNIPER-COS-MIB::jnxCosIfqTxedBytes", ifindex],
                    mib["JUNIPER-COS-MIB::jnxCosIfqTailDropPkts", ifindex],
                ]
            ):
                # ifindex, traffic_class = index.split(".", 1)
                # if ifindex not in ifaces:
                #    continue
                traffic_class = "".join([chr(int(x)) for x in index.split(".")[1:]])
                ts = self.get_ts()
                for metric, value in [
                    ("Interface | CBQOS | Drops | Out | Delta", discards),
                    ("Interface | CBQOS | Octets | Out | Delta", octets),
                    ("Interface | CBQOS | Octets | Out", octets),
                    ("Interface | CBQOS | Packets | Out | Delta", packets),
                    ("Interface | CBQOS | Packets | Out", packets),
                ]:
                    scale = 1
                    self.set_metric(
                        id=(metric, ifaces[ifindex]),
                        metric=metric,
                        value=float(value),
                        ts=ts,
                        labels=ifaces[ifindex] + [f"noc::traffic_class::{traffic_class}"],
                        multi=True,
                        type="delta" if metric.endswith("Delta") else "gauge",
                        scale=scale,
                    )

    def collect_profile_metrics(self, metrics):
        # SLA Metrics
        if self.has_capability("Juniper | RPM | Probes"):
            self.get_ip_sla_udp_jitter_metrics_snmp(
                [m for m in metrics if m.metric in SLA_METRICS_MAP]
            )

    # @metrics(
    #     list(SLA_METRICS_MAP.keys()),
    #     has_capability="Huawei | NQA | Probes",
    #     volatile=True,
    #     access="S",  # CLI version
    # )
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
        for m in metrics:
            if m.metric not in SLA_METRICS_MAP:
                continue
            name = next(
                iter([m.rsplit("::", 1)[-1] for m in m.labels if m.startswith("noc::sla::name::")]),
                None,
            )
            group = next(
                iter(
                    [m.rsplit("::", 1)[-1] for m in m.labels if m.startswith("noc::sla::group::")]
                ),
                None,
            )
            if not name or not group:
                continue
            key = f'{len(group)}.{".".join(str(ord(s)) for s in group)}.{len(name)}.{".".join(str(ord(s)) for s in name)}'
            base = SLA_METRICS_MAP[m.metric]
            if not isinstance(base, tuple):
                oid = mib[
                    base,
                    key,
                    RPMResultCollection.lastCompletedTest.value,
                ]
            else:
                oid = mib[
                    base[0],
                    key,
                    RPMResultCollection.lastCompletedTest.value,
                    base[1],
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
                scale=1 if m.metric != "SLA | Packets | Loss | Ratio" else scale(0.000001),
            )
