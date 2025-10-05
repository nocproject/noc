# ---------------------------------------------------------------------
# Huawei.MA5600T.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import List
from collections import defaultdict

# NOC modules
from noc.sa.profiles.Generic.get_metrics import (
    Script as GetMetricsScript,
    ProfileMetricConfig,
)
from noc.core.models.cfgmetrics import MetricCollectorConfig
from noc.core.text import parse_kv
from noc.core.mib import mib
from .oidrules.gpon_ports import GponPortsRule
from .oidrules.hw_slots import HWSlots
from noc.core.script.metrics import scale

SNMP_UNKNOWN_VALUE = 2147483647


class Script(GetMetricsScript):
    name = "Huawei.MA5600T.get_metrics"

    OID_RULES = [GponPortsRule, HWSlots]

    SENSOR_OID_SCALE = {
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.0.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.0.3": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.0.4": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.1.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.1.1": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.1.2": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.2.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.2.1": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.2.2": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.2.3": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.2.1.9.2.4": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.1.1.5.1.7.0": scale(0.01, 2),
        "1.3.6.1.4.1.2011.6.1.1.5.1.7.1": scale(0.01, 2),
        "1.3.6.1.4.1.2011.6.1.1.5.1.7.2": scale(0.01, 2),
        "1.3.6.1.4.1.2011.6.2.1.2.1.3.0.0.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.2.1.3.1.0.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.2.1.3.2.0.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.3.1.1.0.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.3.1.1.1.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.3.1.1.2.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.3.1.2.0.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.3.1.2.1.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.3.1.2.2.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.6.3.1.4.1.0.0": scale(0.001, 2),
        "1.3.6.1.4.1.2011.6.2.1.6.3.1.6.1.0.0": scale(0.001, 2),
    }

    splitter = re.compile(r"\s*-{3}-+\n")

    kv_map = {
        "rx optical power(dbm)": "Interface | DOM | RxPower",
        "tx optical power(dbm)": "Interface | DOM | TxPower",
        "laser bias current(ma)": "Interface | DOM | Bias Current",
        "temperature(c)": "Interface | DOM | Temperature",
        "voltage(v)": "Interface | DOM | Voltage",
        "olt rx ont optical power(dbm)": "optical_rx_dbm_cpe",
        "upstream frame bip error count": "Interface | DOM | Errors | BIP | Upstream",
        "downstream frame bip error count": "Interface | DOM | Errors | BIP | Downstream",
        "upstream frame hec error count": "Interface | DOM | Errors | HEC | Upstream",
    }

    laser_stats_map = {"Normal": 1}

    CPE_METRICS_CONFIG = {
        "Interface | DOM | Temperature": ProfileMetricConfig(
            metric="Interface | DOM | Temperature",
            oid="HUAWEI-XPON-MIB::hwGponOntOpticalDdmTemperature",
            sla_types=[],
            scale=1,
            units="C",
        ),
        "Interface | DOM | TxPower": ProfileMetricConfig(
            metric="Interface | DOM | TxPower",
            oid="HUAWEI-XPON-MIB::hwGponOntOpticalDdmTxPower",
            sla_types=[],
            scale=scale(0.01, 2),
            units="dBm",
        ),
        "Interface | DOM | RxPower": ProfileMetricConfig(
            metric="Interface | DOM | RxPower",
            oid="HUAWEI-XPON-MIB::hwGponOntOpticalDdmRxPower",
            sla_types=[],
            scale=scale(0.01, 2),
            units="dBm",
        ),
        "Interface | DOM | Voltage": ProfileMetricConfig(
            metric="Interface | DOM | Voltage",
            oid="HUAWEI-XPON-MIB::hwGponOntOpticalDdmVoltage",
            sla_types=[],
            scale=1,
            units="VDC",
        ),
        "Interface | DOM | Bias Current": ProfileMetricConfig(
            metric="Interface | DOM | Bias Current",
            oid="HUAWEI-XPON-MIB::hwGponOntOpticalDdmBiasCurrent",
            sla_types=[],
            scale=1,
            units="m,A",
        ),
        "Interface | DOM | Errors | BIP | Upstream": ProfileMetricConfig(
            metric="Interface | DOM | Errors | BIP | Upstream",
            oid="HUAWEI-XPON-MIB::hwGponOntTrafficFlowStatisticUpFrameBipErrCnt",
            sla_types=[],
            scale=1,
            units="1",
        ),
        "Interface | DOM | Errors | BIP | Upstream | Delta": ProfileMetricConfig(
            metric="Interface | DOM | Errors | BIP | Upstream",
            oid="HUAWEI-XPON-MIB::hwGponOntTrafficFlowStatisticUpFrameBipErrCnt",
            sla_types=[],
            scale=1,
            units="1",
        ),
        "Interface | DOM | Errors | HEC | Upstream": ProfileMetricConfig(
            metric="Interface | DOM | Errors | HEC | Upstream",
            oid="",
            sla_types=[],
            scale=1,
            units="1",
        ),
        "Interface | DOM | Errors | HEC | Upstream | Delta": ProfileMetricConfig(
            metric="Interface | DOM | Errors | HEC | Upstream",
            oid="",
            sla_types=[],
            scale=1,
            units="1",
        ),
        "Interface | DOM | Errors | BIP | Downstream": ProfileMetricConfig(
            metric="Interface | DOM | Errors | BIP | Downstream",
            oid="HUAWEI-XPON-MIB::hwGponOntTrafficFlowStatisticDnFramesBipErrCnt",
            sla_types=[],
            scale=1,
            units="1",
        ),
        "Interface | DOM | Errors | BIP | Downstream | Delta": ProfileMetricConfig(
            metric="Interface | DOM | Errors | BIP | Downstream",
            oid="HUAWEI-XPON-MIB::hwGponOntTrafficFlowStatisticDnFramesBipErrCnt",
            sla_types=[],
            scale=1,
            units="1",
        ),
    }

    def get_cpe_metrics(self, metrics: List[MetricCollectorConfig]):
        ont_ifaces = defaultdict(list)
        ts = self.get_ts()
        # Group metric by port
        for probe in metrics:
            hints = probe.get_hints()
            frame, slot, port, ont_id = hints["local_id"].split("/")
            ont_ifaces[(frame, slot)] += [(probe, frame, slot, port, ont_id)]
        if not ont_ifaces:
            return
        self.cli("config")
        for iface, ont_ids in ont_ifaces.items():
            self.cli("interface gpon %s/%s" % iface)  # Fix from cpes
            for probe, frame, slot, port, ont_id in ont_ids:
                v = self.cli(f"display ont optical-info {port} {ont_id}")
                results = parse_kv(self.kv_map, v)
                v = self.cli(f"display statistics ont-line-quality {port} {ont_id}")
                results.update(parse_kv(self.kv_map, v))
                for m, mc in self.CPE_METRICS_CONFIG.items():
                    if mc.metric not in results or results[mc.metric] == "-":
                        continue
                    self.set_metric(
                        id=probe.cpe,
                        cpe=probe.cpe,
                        metric=m,
                        value=float(results[mc.metric]),
                        ts=ts,
                        labels=[*probe.labels, "noc::interface::0"],
                        multi=True,
                        type="gauge",
                        scale=1,
                        units=mc.units,
                    )
                if "optical_rx_dbm_cpe" in results and results["optical_rx_dbm_cpe"] != "-":
                    self.set_metric(
                        id=probe.cpe,
                        cpe=probe.cpe,
                        metric="Interface | DOM | RxPower",
                        value=float(results["optical_rx_dbm_cpe"]),
                        ts=ts,
                        labels=[
                            *probe.labels,
                            f"noc::interface::{frame}/{slot}/{port}",
                            f"noc::subinterface::{frame}/{slot}/{port}/{ont_id}",
                        ],
                        multi=True,
                        type="gauge",
                        scale=1,
                        units="dBm",
                    )

        self.cli("quit")
        self.cli("quit")

    def collect_cpe_metrics(self, metrics: List[MetricCollectorConfig]):
        if self.get_access_preference().startswith("C"):
            return self.get_cpe_metrics(metrics)
        oids = {}
        ts = self.get_ts()
        self.logger.info("Collect CPE Metrics: %s", metrics)
        for probe in metrics:
            # if m.metric not in self.SLA_METRICS_CONFIG:
            #    continue
            hints = probe.get_hints()
            _, ont_id = hints["local_id"].rsplit("/", 1)
            for m in probe.metrics:
                if m not in self.CPE_METRICS_CONFIG:
                    continue
                mc = self.CPE_METRICS_CONFIG[m]
                if not mc.oid:
                    continue
                oid = mib[mc.oid, hints.get("ifindex"), ont_id]
                oids[oid] = (probe, mc)
        # mib["HUAWEI-XPON-MIB::hwGponOntOpticalDdmOltRxOntPower"],
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        for r in results:
            if results[r] is None or results[r] == SNMP_UNKNOWN_VALUE:
                continue
            probe, mc = oids[r]
            self.set_metric(
                id=probe.cpe,
                cpe=probe.cpe,
                metric=mc.metric,
                value=float(results[r]),
                ts=ts,
                labels=probe.labels,
                multi=True,
                type="gauge",
                scale=mc.scale,
                units=mc.units,
            )
