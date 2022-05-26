# ---------------------------------------------------------------------
# Huawei.MA5600T.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
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

    kv_map = {
        "rx optical power(dbm)": "optical_rx_dbm",
        "tx optical power(dbm)": "optical_tx_dbm",
        "laser bias current(ma)": "current_ma",
        "temperature(c)": "temp_c",
        "voltage(v)": "voltage_v",
        "olt rx ont optical power(dbm)": "optical_rx_dbm_cpe",
        "upstream frame bip error count": "optical_errors_bip_out",
        "downstream frame bip error count": "optical_errors_bip_in",
    }

    @metrics(
        [
            "Interface | DOM | RxPower",
            "Interface | DOM | TxPower",
            "Interface | DOM | Voltage",
            "Interface | DOM | Bias Current",
            "Interface | DOM | Temperature",
            "Interface | Errors | BIP | In",
            "Interface | Errors | BIP | Out",
        ],
        has_capability="Network | PON | OLT",
        access="C",  # CLI version
        volatile=False,
    )
    def collect_dom_metrics_cli(self, metrics):
        super().collect_dom_metrics(metrics)
        self.collect_cpe_metrics_cli(metrics)

    def collect_cpe_metrics_cli(self, metrics):
        # ifaces = set(m.path[-1].split("/")[:2] for m in metrics)
        onts = self.scripts.get_cpe_status()  # Getting ONT List
        self.cli("config")
        iface = None
        for cc in sorted(onts, key=lambda x: x["interface"].split("/")):
            if cc.get("status", "") != "active":
                continue
            frame, slot, port, cpe_id = cc["id"].split("/")
            if iface != (frame, slot):
                if iface is not None:
                    self.cli("quit")
                iface = (frame, slot)
                self.cli("interface gpon %s/%s" % iface)  # Fix from cpes
            ipath = [f'noc::chassis::{cc["global_id"]}', "noc::interface::0"]
            mpath = [f'noc::interface::{"/".join([frame, slot, port])}']
            v = self.cli("display ont optical-info %s %s" % (port, cpe_id))
            m = parse_kv(self.kv_map, v)

            self.logger.debug("Collect %s, %s, %s", m, ipath, mpath)
            if m.get("temp_c", "-") != "-":
                self.set_metric(
                    id=("Interface | DOM | Temperature", mpath),
                    metric="Interface | DOM | Temperature",
                    labels=ipath,
                    value=float(m["temp_c"]),
                    multi=True,
                )
            if m.get("voltage_v", "-") != "-":
                self.set_metric(
                    id=("Interface | DOM | Voltage", mpath),
                    metric="Interface | DOM | Voltage",
                    labels=ipath,
                    value=float(m["voltage_v"]),
                    multi=True,
                )
            if m.get("optical_rx_dbm", "-") != "-":
                self.set_metric(
                    id=("Interface | DOM | RxPower", mpath),
                    metric="Interface | DOM | RxPower",
                    labels=ipath,
                    value=float(m["optical_rx_dbm"]),
                    multi=True,
                )
            if m.get("optical_rx_dbm_cpe", "-") != "-":
                self.set_metric(
                    id=("Interface | DOM | RxPower", mpath),
                    metric="Interface | DOM | RxPower",
                    labels=[f'noc::interface::{cc["interface"]}', f'noc::subinterface::{cc["id"]}'],
                    value=float(
                        m["optical_rx_dbm_cpe"]
                        if "," not in m["optical_rx_dbm_cpe"]
                        else m["optical_rx_dbm_cpe"].split(",")[0]
                    ),
                    multi=True,
                )
            if m.get("current_ma", "-") != "-":
                self.set_metric(
                    id=("Interface | DOM | Bias Current", mpath),
                    metric="Interface | DOM | Bias Current",
                    labels=ipath,
                    value=float(m["current_ma"]),
                    multi=True,
                )
            if m.get("optical_tx_dbm", "-") != "-":
                self.set_metric(
                    id=("Interface | DOM | TxPower", mpath),
                    metric="Interface | DOM | TxPower",
                    labels=ipath,
                    value=float(m["optical_tx_dbm"]),
                    multi=True,
                )
            v = self.cli("display statistics ont-line-quality %s %s" % (port, cpe_id))
            m = parse_kv(self.kv_map, v)
            if m.get("optical_errors_bip_out", "-") != "-":
                self.set_metric(
                    id=("Interface | Errors | BIP | Out", mpath),
                    metric="Interface | Errors | BIP | Out",
                    labels=ipath,
                    value=int(m["optical_errors_bip_out"]),
                    multi=True,
                )
            if m.get("optical_errors_bip_in", "-") != "-":
                self.set_metric(
                    id=("Interface | Errors | BIP | In", mpath),
                    metric="Interface | Errors | BIP | In",
                    labels=ipath,
                    value=int(m["optical_errors_bip_in"]),
                    multi=True,
                )

        self.cli("quit")
        self.cli("quit")

    @metrics(
        [
            "Interface | DOM | RxPower",
            "Interface | DOM | TxPower",
            "Interface | DOM | Voltage",
            "Interface | DOM | Bias Current",
            "Interface | DOM | Temperature",
            "Interface | Errors | BIP | In",
            "Interface | Errors | BIP | Out",
        ],
        has_capability="Network | PON | OLT",
        access="S",  # CLI version
        volatile=False,
    )
    def collect_dom_metrics_snmp(self, metrics):
        super().collect_dom_metrics(metrics)
        self.collect_cpe_metrics_snmp(metrics)

    def collect_cpe_metrics_snmp(self, metrics):
        names = {x: y for y, x in self.scripts.get_ifindexes(name_oid="IF-MIB::ifName").items()}
        global_id_map = {}
        for ont_index, ont_serial in self.snmp.get_tables(
            [mib["HUAWEI-XPON-MIB::hwGponDeviceOntSn"]]
        ):
            global_id_map[ont_index] = ont_serial.encode("hex").upper()
        for (
            ont_index,
            ont_temp_c,
            ont_current_ma,
            ont_optical_tx_dbm,
            ont_optical_rx_dbm,
            ont_voltage_v,
            optical_rx_dbm_cpe,
        ) in self.snmp.get_tables(
            [
                mib["HUAWEI-XPON-MIB::hwGponOntOpticalDdmTemperature"],
                mib["HUAWEI-XPON-MIB::hwGponOntOpticalDdmBiasCurrent"],
                mib["HUAWEI-XPON-MIB::hwGponOntOpticalDdmTxPower"],
                mib["HUAWEI-XPON-MIB::hwGponOntOpticalDdmRxPower"],
                mib["HUAWEI-XPON-MIB::hwGponOntOpticalDdmVoltage"],
                mib["HUAWEI-XPON-MIB::hwGponOntOpticalDdmOltRxOntPower"],
            ],
            bulk=False,
        ):
            ifindex, ont_id = ont_index.split(".")
            ont_id = f"{names[int(ifindex)]}/{ont_id}"
            ipath = [f"noc::chassis::{global_id_map[ont_index]}", "noc::interface::0"]
            mpath = [f"noc::interface::{names[int(ifindex)]}"]
            if ont_temp_c != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | DOM | Temperature", mpath),
                    metric="Interface | DOM | Temperature",
                    labels=ipath,
                    value=float(ont_temp_c),
                    multi=True,
                )
            if ont_current_ma != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | DOM | Bias Current", mpath),
                    metric="Interface | DOM | Bias Current",
                    labels=ipath,
                    value=float(ont_current_ma),
                    multi=True,
                )
            if ont_voltage_v != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | DOM | Voltage", mpath),
                    metric="Interface | DOM | Voltage",
                    labels=ipath,
                    value=float(ont_voltage_v),
                    multi=True,
                )
            if ont_optical_tx_dbm != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | DOM | TxPower", mpath),
                    metric="Interface | DOM | TxPower",
                    labels=ipath,
                    value=float(ont_optical_tx_dbm) / 100.0,
                    multi=True,
                )
            if ont_optical_rx_dbm != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | DOM | RxPower", mpath),
                    metric="Interface | DOM | RxPower",
                    labels=ipath,
                    value=float(ont_optical_rx_dbm) / 100.0,
                    multi=True,
                )
            if optical_rx_dbm_cpe != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | DOM | RxPower", mpath),
                    metric="Interface | DOM | RxPower",
                    labels=[
                        f"noc::interface::{names[int(ifindex)]}",
                        f"noc::subinterface::{ont_id}",
                    ],
                    value=float(optical_rx_dbm_cpe) / 100.0,
                    multi=True,
                )
        for (
            ont_index,
            ont_optical_errors_bip_out,
            ont_optical_errors_bip_in,
        ) in self.snmp.get_tables(
            [
                mib["HUAWEI-XPON-MIB::hwGponOntTrafficFlowStatisticUpFrameBipErrCnt"],
                mib["HUAWEI-XPON-MIB::hwGponOntTrafficFlowStatisticDnFramesBipErrCnt"],
            ],
            bulk=False,
        ):
            ifindex, ont_id = ont_index.split(".")
            ipath = [f"noc::chassis::{global_id_map[ont_index]}", "noc::interface::0"]
            mpath = [f"noc::interface::{names[int(ifindex)]}"]
            if ont_optical_errors_bip_out != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | Errors | BIP | Out", mpath),
                    metric="Interface | Errors | BIP | Out",
                    labels=ipath,
                    value=int(ont_optical_errors_bip_out),
                    multi=True,
                )
            if ont_optical_errors_bip_in != SNMP_UNKNOWN_VALUE:
                self.set_metric(
                    id=("Interface | Errors | BIP | In", mpath),
                    metric="Interface | Errors | BIP | In",
                    labels=ipath,
                    value=int(ont_optical_errors_bip_in),
                    multi=True,
                )
