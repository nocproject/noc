# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus
from noc.lib.text import parse_table, parse_kv


class Script(BaseScript):
    name = "Huawei.VRP.get_dom_status"
    interface = IGetDOMStatus

    rx_port = re.compile(
        "Port (?P<port>\S+\d+) transceiver diagnostic information:")

    ne_map = {
        "tx power": "tx_power",
        "rx power": "rx_power"
    }

    def parse_ports(self, s):
        match = self.rx_port.search(s)
        if match:
            port = match.group("port")
            obj = match.groupdict()
            return port, obj, s[match.end():]
        else:
            return None

    def execute_ne(self, interface=None):
        """

        :param interface:
        :return:
        """
        cmd = "display interface phy-option"
        if interface is not None:
            cmd += " %s" % interface
        try:
            c = self.cli(cmd)
        except self.CLISyntaxError:
            return []
        r = []
        for block in c.split("\n\n"):
            if "transceiver offline" in block:
                continue
            iface = {"interface": block.splitlines()[0]}
            res = parse_kv(self.ne_map, block)
            if "rx_power" in res:
                # Rx Power: -10.44dBm, Warning range: [-17.011,  0.000]dBm
                iface["optical_rx_dbm"] = float(res["rx_power"].split(",")[0][:-3])
            if "tx_power" in res:
                # Tx Power:   3.35dBm, Warning range: [0.999,  5.000]dBm
                iface["optical_tx_dbm"] = float(res["tx_power"].split(",")[0][:-3])
            r += [iface]
        return r

    def execute(self, interface=None):
        if self.is_ne_platform:
            return self.execute_ne(interface=interface)
        cmd = "display transceiver diagnosis interface"
        if interface is not None:
            cmd += " %s" % interface
        try:
            c = self.cli(cmd)
        except self.CLISyntaxError:
            return []

        r = []
        for block in c.split("\n\n"):
            match = self.rx_port.search(block)
            if match:
                iface = {"interface": match.group("port")}
                t = parse_table(block)
                for i in t:
                    if i[0] == "TxPower(dBm)":
                        iface["optical_tx_dbm"] = i[1]
                    if i[0] == "RxPower(dBm)":
                        iface["optical_rx_dbm"] = i[1]
                    if i[0] == "Current(mA)":
                        iface["current_ma"] = i[1]
                    if i[0] == "Temp.(C)":
                        iface["temp_c"] = i[1]
                    if i[0] == "Voltage(V)":
                        iface["voltage_v"] = i[1]
                if t:
                    r += [iface]
        return r
