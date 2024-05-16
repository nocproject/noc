# ---------------------------------------------------------------------
# Juniper.JUNOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
from typing import List
import enum

# NOC modules
from noc.sa.profiles.Generic.get_metrics import (
    Script as GetMetricsScript,
    metrics,
    ProfileMetricConfig,
)
from noc.core.models.cfgmetrics import MetricCollectorConfig
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
    currentTest = 1
    lastCompletedTest = 2
    movingAverage = 3
    allTests = 4


class Script(GetMetricsScript):
    name = "Juniper.JUNOS.get_metrics"
    OID_RULES = [SlotRule]
    SLA_METRICS_CONFIG = {
        "SLA | Packets": ProfileMetricConfig(
            metric="SLA | Packets",
            oid="JUNIPER-RPM-MIB::jnxRpmResSumSent",
            sla_types=["udp-jitter", "icmp-echo"],
            scale=1,
            units="pkt",
        ),
        "SLA | Packets | Loss | Ratio": ProfileMetricConfig(
            metric="SLA | Packets | Loss | Ratio",
            oid="JUNIPER-RPM-MIB::jnxRpmResSumPercentLost",
            sla_types=["udp-jitter", "icmp-echo"],
            scale=scale(0.000001),
            units="%",
        ),
        # Jitter
        "SLA | Jitter | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | Avg",
            oid=("JUNIPER-RPM-MIB::jnxRpmResCalcAverage", 4),
            sla_types=["udp-jitter", "icmp-echo"],
            scale=scale(0.001),
            units="m,s",
        ),
        "SLA | Jitter | Out | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | Out | Avg",
            oid=("JUNIPER-RPM-MIB::jnxRpmResCalcAverage", RPMMeasurement.egress.value),
            sla_types=["udp-jitter", "icmp-echo"],
            scale=scale(0.001),
            units="m,s",
        ),
        "SLA | Jitter | In | Avg": ProfileMetricConfig(
            metric="SLA | Jitter | In | Avg",
            oid=("JUNIPER-RPM-MIB::jnxRpmResCalcAverage", RPMMeasurement.ingress.value),
            sla_types=["udp-jitter", "icmp-echo"],
            scale=scale(0.001),
            units="m,s",
        ),
        #
        "SLA | RTT | Min": ProfileMetricConfig(
            metric="SLA | RTT | Min",
            oid=("JUNIPER-RPM-MIB::jnxRpmResCalcMin", RPMMeasurement.roundTripTime.value),
            sla_types=["udp-jitter", "icmp-echo"],
            scale=scale(0.001),
            units="m,s",
        ),
        "SLA | RTT | Max": ProfileMetricConfig(
            metric="SLA | RTT | Max",
            oid=("JUNIPER-RPM-MIB::jnxRpmResCalcMax", RPMMeasurement.roundTripTime.value),
            sla_types=["udp-jitter", "icmp-echo"],
            scale=scale(0.001),
            units="m,s",
        ),
    }

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
        ifaces = {m.ifindex: m for m in metrics if m.ifindex}
        for ifindex in ifaces:
            for (index, out_packets, out_octets, discards) in self.snmp.get_tables(
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
                    ("Interface | CBQOS | Octets | Out | Delta", out_octets),
                    ("Interface | CBQOS | Octets | Out", out_octets),
                    ("Interface | CBQOS | Packets | Out | Delta", out_packets),
                    ("Interface | CBQOS | Packets | Out", out_packets),
                ]:
                    if not value:
                        continue
                    scale = 1
                    sc = ifaces[ifindex]
                    self.set_metric(
                        id=(metric, sc.labels),
                        metric=metric,
                        value=float(value),
                        ts=ts,
                        labels=sc.labels + [f"noc::traffic_class::{traffic_class}"],
                        multi=True,
                        type="delta" if metric.endswith("Delta") else "gauge",
                        scale=scale,
                        units="byte" if "Octets" in metric else "pkt",
                        service=sc.service,
                    )

    def collect_sla_metrics(self, metrics):
        # SLA Metrics
        if self.has_capability("Juniper | RPM | Probes"):
            self.get_ip_sla_udp_jitter_metrics_snmp(metrics)

    # @metrics(
    #     list(SLA_METRICS_MAP.keys()),
    #     has_capability="Huawei | NQA | Probes",
    #     volatile=True,
    #     access="S",  # CLI version
    # )
    def get_ip_sla_udp_jitter_metrics_snmp(self, metrics: List[MetricCollectorConfig]):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        oids = {}
        # stat_index = 250
        for probe in metrics:
            hints = probe.get_hints()
            name = hints["sla_name"]
            group = hints["sla_group"]
            if not name or not group:
                continue
            key = (
                f'{len(group)}.{".".join(str(ord(s)) for s in group)}.'
                f'{len(name)}.{".".join(str(ord(s)) for s in name)}'
            )
            for m in probe.metrics:
                if m not in self.SLA_METRICS_CONFIG:
                    continue
                mc = self.SLA_METRICS_CONFIG[m]
                if not isinstance(mc.oid, tuple):
                    oid = mib[
                        mc.oid,
                        key,
                        RPMResultCollection.lastCompletedTest.value,
                    ]
                else:
                    oid = mib[
                        mc.oid[0],
                        key,
                        RPMResultCollection.lastCompletedTest.value,
                        mc.oid[1],
                    ]
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

    def get_dict_dhcp_pool_name_IP(self):
        """
        Prepare dict for labels.
        {snmp_index:
            {
                snmp_index: str,
                pool_name: str,
                ip: str,
                ipv6: bool,
                prefix: Option(str) # only for ipv6
            }
        }
        """
        result = {}
        pool_name_oid = "1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.3"  # jnxUserAAAAccessPoolName
        for oid, v in self.snmp.getnext(pool_name_oid, bulk=False):
            snmp_index = oid.split(pool_name_oid, 1)[-1][1:]
            result[snmp_index] = {
                "snmp_index": snmp_index,
                "pool_name": str(v),
            }

        pool_ip_oid = "1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.6"  # jnxUserAAAAccessPoolInetNetwork
        for oid, v in self.snmp.getnext(pool_ip_oid, bulk=False):
            snmp_index = oid.split(pool_ip_oid, 1)[-1][1:]
            if result.get(snmp_index):
                result[snmp_index].update({"ip": v})

        pool_ip_prefix = (
            "1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.7"  # jnxUserAAAAccessPoolInetPrefixLength
        )
        for oid, v in self.snmp.getnext(pool_ip_prefix, bulk=False):
            snmp_index = oid.split(pool_ip_prefix, 1)[-1][1:]
            if result.get(snmp_index) and v != 0:
                result[snmp_index].update({"ipv6": True, "prefix": v})
            else:
                result[snmp_index].update({"ipv6": False})
        return result

    def get_metric_value(self, oid_in: str, dhcp_pool_param: dict):
        for oid, v in self.snmp.getnext(oid_in, bulk=False):
            snmp_index = oid.split(oid_in, 1)[-1][1:]
            param = dhcp_pool_param.get(snmp_index)
            if param:
                pool = param["pool_name"]
                pool_ip = param["ip"]
                pool_ip = pool_ip.replace("::", ";;")  # :: use in separate scope, dont show in card
                if param["ipv6"]:
                    pool_ip += f"/{param['prefix']}"
                yield pool, pool_ip, v
            yield None, None, None

    @metrics(
        [
            "DHCP | Pool | Leases | Active",
            "DHCP | Pool | Leases | Total",
            "DHCP | Pool | Leases | Active | Percent",
        ],
        has_capability="Network | DHCP",
        volatile=False,
        access="S",  # not CLI version
    )
    def get_lease_metrics(self, metrics):
        dhcp_pool_param = self.get_dict_dhcp_pool_name_IP()
        #  jnxUserAAAAccessPoolAddressesInUse 1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.11
        for pool, pool_ip, v in self.get_metric_value(
            "1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.11", dhcp_pool_param
        ):
            if pool and pool_ip:
                self.set_metric(
                    id=("DHCP | Pool | Leases | Active", None),
                    labels=[
                        f"noc::ippool::name::{pool}",
                        f"noc::ippool::prefix::{pool_ip}",
                        "noc::ippool::type::dhcp",
                    ],
                    value=v,
                    multi=True,
                )
        # jnxUserAAAAccessPoolAddressTotal 1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.10
        for pool, pool_ip, v in self.get_metric_value(
            "1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.10", dhcp_pool_param
        ):
            if pool and pool_ip:
                self.set_metric(
                    id=("DHCP | Pool | Leases | Total", None),
                    labels=[
                        f"noc::ippool::name::{pool}",
                        f"noc::ippool::prefix::{pool_ip}",
                        "noc::ippool::type::dhcp",
                    ],
                    value=v,
                    multi=True,
                )
        # jnxUserAAAAccessPoolAddressUsage 1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.12
        for pool, pool_ip, v in self.get_metric_value(
            "1.3.6.1.4.1.2636.3.51.1.1.4.1.1.1.12", dhcp_pool_param
        ):
            if pool and pool_ip and int(v) < 101:
                self.set_metric(
                    id=("DHCP | Pool | Leases | Active | Percent", None),
                    labels=[
                        f"noc::ippool::name::{pool}",
                        f"noc::ippool::prefix::{pool_ip}",
                        "noc::ippool::type::dhcp",
                    ],
                    value=v,
                    multi=True,
                    units="%",
                )
