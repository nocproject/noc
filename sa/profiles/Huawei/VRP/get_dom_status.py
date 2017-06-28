# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Huawei.VRP.get_dom_status"
    interface = IGetDOMStatus

    rx_port = re.compile(
        "Port (?P<port>\S+\d+) transceiver diagnostic information:")

    def parse_ports(self, s):
        match = self.rx_port.search(s)
        if match:
            port = match.group("port")
            obj = match.groupdict()
            return port, obj, s[match.end():]
        else:
            return None

    def execute(self, interface=None):
        cmd = "display transceiver diagnosis interface"
        if interface is not None:
            cmd += "%s" % interface
        try:
            c = self.cli(cmd)
        except self.CLISyntaxError:
            return []

        r = []
        for l in c.split("\n\n"):
            match = self.rx_port.search(l)
            if match:
                iface = { "interface": match.group("port") }
                t = parse_table(l)
                for i in t:
                    if i[0] == "TxPower(dBm)":
                         iface["optical_tx_dbm"]= i[1]
                    if i[0] == "RxPower(dBm)":
                         iface["optical_rx_dbm"]= i[1]
                    if i[0] == "Current(mA)":
                         iface["current_ma"]= i[1]
                    if i[0] == "Temp.(C)":
                         iface["temp_c"]= i[1]
                    if i[0] == "Voltage(V)":
                         iface["voltage_v"]= i[1]
                if t:
                    r += [iface]
        return r
