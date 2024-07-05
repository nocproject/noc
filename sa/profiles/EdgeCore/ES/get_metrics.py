# ---------------------------------------------------------------------
# EdgeCore.ES.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_metrics import (
    Script as GetMetricsScript,
    metrics,
    ProfileMetricConfig,
)
from noc.core.text import parse_kv, parse_table


class Script(GetMetricsScript):
    name = "EdgeCore.ES.get_metrics"

    metric_map = {
        "CRC Align Errors": "Interface | Errors | CRC",
        "Frames Too Long": "Interface | Errors | Frame",
    }

    rx_ddm = re.compile(r"DDM Info")

    ddm_map = {
        "temperature": "Interface | DOM | Temperature",
        "vcc": "Interface | DOM | Voltage",
        "bias current": "Interface | DOM | Bias Current",
        "tx power ": "Interface | DOM | TxPower",
        "rx power ": "Interface | DOM | RxPower",
    }

    ddm_map_4226 = {
        "Interface | DOM | Temperature": 1,
        "Interface | DOM | Voltage": 2,
        "Interface | DOM | Bias Current": 3,
        "Interface | DOM | RxPower": 4,
        "Interface | DOM | TxPower": 5,
    }

    CPE_METRICS_CONFIG = {
        "Interface | DOM | Temperature": ProfileMetricConfig(
            metric="Interface | DOM | Temperature",
            oid="",
            sla_types=[],
            scale=1,
            units="C",
        ),
        "Interface | DOM | TxPower": ProfileMetricConfig(
            metric="Interface | DOM | TxPower",
            oid="",
            sla_types=[],
            scale=1,
            units="dBm",
        ),
        "Interface | DOM | RxPower": ProfileMetricConfig(
            metric="Interface | DOM | RxPower",
            oid="",
            sla_types=[],
            scale=1,
            units="dBm",
        ),
        "Interface | DOM | Voltage": ProfileMetricConfig(
            metric="Interface | DOM | Voltage",
            oid="",
            sla_types=[],
            scale=1,
            units="VDC",
        ),
        "Interface | DOM | Bias Current": ProfileMetricConfig(
            metric="Interface | DOM | Bias Current",
            oid="",
            sla_types=[],
            scale=1,
            units="m,A",
        ),
    }

    DOM_METRIC_INDEX = {
        "Interface | DOM | Temperature": 2,
        "Interface | DOM | Voltage": 3,
        "Interface | DOM | Bias Current": 4,
        "Interface | DOM | TxPower": 5,
        "Interface | DOM | RxPower": 6,
    }

    DOM_OID_3510 = "1.3.6.1.4.1.259.10.1.27.1.2.11.1"

    # @metrics(
    #     ["Interface | Errors | CRC", "Interface | Errors | Frame"],
    #     has_capability="DB | Interfaces",
    #     volatile=False,
    #     access="C",
    # )
    # def get_errors_interface_metrics(self, metrics):
    #     v = self.cli("show interfaces counters")
    #     v = self.profile.parse_ifaces(v)
    #
    #     ts = self.get_ts()
    #     print(v)
    #     for metric in self.metric_map:
    #         for iface in v:
    #             if metric not in v[iface]:
    #                 continue
    #             self.set_metric(
    #                 id=(metric, f"noc::interface::{self.profile.convert_interface_name(iface)}"),
    #                 metric=metric,
    #                 labels=[f"noc::interface::{self.profile.convert_interface_name(iface)}"],
    #                 value=int(v[iface][metric]),
    #                 ts=ts,
    #                 multi=True,
    #                 units="pkt",
    #             )
    #

    @metrics(["Object | MAC | TotalUsed"], access="S")  # SNMP version
    def get_count_mac_snmp(self, metrics):
        mac_total_used = 0
        for _, mac_num in self.snmp.getnext("1.3.6.1.2.1.17.7.1.2.1.1.2"):
            if mac_num:
                mac_total_used += mac_num
        if mac_total_used:
            self.set_metric(id=("Object | MAC | TotalUsed", None), value=int(mac_total_used))

    def get_trans_metrics_4626(self, iname, ilabel):
        try:
            v = self.cli(f"show transceiver interface {iname}")
            res = parse_table(v)
            if res:
                for m, mc in self.CPE_METRICS_CONFIG.items():
                    metric_value = res[0][self.ddm_map_4226[m]].strip()
                    if metric_value and metric_value != "N/A":
                        self.set_metric(
                            id=(m, ilabel),
                            metric=m,
                            value=float(metric_value.split()[0]),
                            labels=ilabel,
                            multi=True,
                            type="gauge",
                            units=mc.units,
                        )
        except self.CLISyntaxError:
            raise NotImplementedError

    @metrics(
        [
            "Interface | DOM | Temperature",
            "Interface | DOM | Bias Current",
            "Interface | DOM | TxPower",
            "Interface | DOM | RxPower",
            "Interface | DOM | Voltage",
        ],
        access="C",
        volatile=False,
    )  # CLI version
    def get_optical_transciever_metrics_cli(self, metrics):
        for iface in metrics:
            ilabels = iface.labels
            iname = ilabels[0].split("::")[-1]
            if self.is_platform_4626:
                self.get_trans_metrics_4626(iname, ilabels)
            else:
                try:
                    v = self.cli(f"show interfaces transceiver {iname}")
                    match = self.rx_ddm.search(v)
                    if match:
                        res = parse_kv(self.ddm_map, v)
                        if res:
                            for m, mc in self.CPE_METRICS_CONFIG.items():
                                if m in res:
                                    self.set_metric(
                                        id=(m, ilabels),
                                        metric=m,
                                        value=float(res[m].split()[0]),
                                        labels=ilabels,
                                        multi=True,
                                        type="gauge",
                                        units=mc.units,
                                    )
                except self.CLISyntaxError:
                    raise NotImplementedError

    @metrics(
        [
            "Interface | DOM | Temperature",
            "Interface | DOM | Bias Current",
            "Interface | DOM | TxPower",
            "Interface | DOM | RxPower",
            "Interface | DOM | Voltage",
        ],
        access="S",
        volatile=False,
        matcher="is_platform_ecs3510",
    )  # SNMP version
    def get_optical_transciever_metrics_snmp(self, metrics):
        for iface in metrics:
            ilabels = iface.labels
            ifindex = iface.ifindex
            metric = iface.metric
            metric_index = self.DOM_METRIC_INDEX[metric]
            mertic_oid = f"{self.DOM_OID_3510}.{metric_index}.{ifindex}"
            v = self.snmp.get(mertic_oid)
            metric_unit = self.CPE_METRICS_CONFIG.get(metric).units
            if v:
                self.set_metric(
                    id=(metric, ilabels),
                    metric=metric,
                    value=float(v.split()[0]),
                    labels=ilabels,
                    multi=True,
                    type="gauge",
                    units=metric_unit,
                )
