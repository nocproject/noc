# ---------------------------------------------------------------------
# Huawei.MA5600T.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.MA5600T.get_dom_status"
    interface = IGetDOMStatus

    splitter = re.compile(r"\s*-{3}-+\n")

    def execute_cli(self, interface=None, **kwargs):
        interfaces = [interface] if interface else []
        if not interface:
            _, boards = self.profile.get_board(self)
            for board in boards:
                if board["type"] == "GPON" and board["status"] == "Normal":
                    interfaces += ["0/%s/0" % board["num"]]
        r = []
        for iface in interfaces:
            self.cli("config")
            frame, slot, port = iface.split("/")
            self.cli("interface gpon %s/%s" % (frame, slot))  # Fix from cpes
            r = []
            v = self.cli("display port state all")
            for port in self.splitter.split(v):
                port = {
                    line.rsplit(None, 1)[0].strip(): line.rsplit(None, 1)[1].strip()
                    for line in port.splitlines()
                    if len(line.rsplit(None, 1)) == 2
                }
                if not port:
                    continue
                if port["Port state"] == "Offline":
                    self.logger.info("Port %s is offline mode" % port["Port state"])
                    continue
                r += [
                    {
                        "interface": port["F/S/P"],
                        "temp_c": float(port["Temperature(C)"]),
                        "voltage_v": float(port["Supply Voltage(V)"]),
                        "current_ma": float(port["TX Bias current(mA)"]),
                        "optical_tx_dbm": float(port["TX power(dBm)"]),
                        "optical_rx_dbm": float(port["RX power(dBm)"]),
                    }
                ]
            self.cli("quit")
            self.cli("quit")
        return r

    def execute_snmp(self, interface=None, **kwargs):
        r = []
        names = {v: k for k, v in self.scripts.get_ifindexes(name_oid="IF-MIB::ifName").items()}
        for (
            olt_index,
            olt_temp_c,
            olt_voltage_v,
            olt_current_ma,
            olt_optical_tx_dbm,
            olt_optical_rx_dbm,
        ) in self.snmp.get_tables(
            [
                mib["HUAWEI-XPON-MIB::hwGponOltOpticsDdmInfoTemperature"],
                mib["HUAWEI-XPON-MIB::hwGponOltOpticsDdmInfoSupplyVoltage"],
                mib["HUAWEI-XPON-MIB::hwGponOltOpticsDdmInfoTxBiasCurrent"],
                mib["HUAWEI-XPON-MIB::hwGponOltOpticsDdmInfoTxPower"],
                mib["HUAWEI-XPON-MIB::hwGponOltOpticsDdmInfoRxPower"],
            ],
            bulk=False,
        ):
            if olt_temp_c == 2147483647:
                continue
            iface_index = olt_index.rsplit(".", 1)[-1]
            r += [
                {
                    "interface": names[int(iface_index)],
                    "temp_c": float(olt_temp_c),
                    "voltage_v": float(olt_voltage_v),
                    "current_ma": float(olt_current_ma),
                    "optical_tx_dbm": float(olt_optical_tx_dbm) / 100.0,
                    "optical_rx_dbm": (
                        float(olt_optical_rx_dbm) / 100.0 if olt_optical_rx_dbm != 2147483647 else 0
                    ),
                }
            ]
        return r
