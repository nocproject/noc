# ---------------------------------------------------------------------
# DLink.DxS.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus


class Script(BaseScript):
    name = "DLink.DxS.get_dom_status"
    interface = IGetDOMStatus

    rx_port = re.compile(
        r"^\s+(?P<port>\d+\S*)\s+(?P<temp>\S+)\s+(?P<volt>\S+)\s+"
        r"(?P<bias>\S+)\s+(?P<txpw>\S+)\s+(?P<rxpw>\S+)\s*$",
        re.MULTILINE,
    )

    def parse_ports(self, s):
        match = self.rx_port.search(s)
        if match:
            port = match.group("port")
            obj = match.groupdict()
            return port, obj, s[match.end() :]
        else:
            return None

    def execute_cli(self, interface=None):
        cmd = "show ddm ports status"
        if interface is not None:
            cmd = "show ddm ports %s status" % interface
        try:
            ports = self.cli(cmd, obj_parser=self.parse_ports, cmd_next="n", cmd_stop="q")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for i in ports:
            temp_c = i["temp"]
            if temp_c == "-":
                temp_c = None
            voltage_v = i["volt"]
            if voltage_v == "-":
                voltage_v = None
            current_ma = i["bias"]
            if current_ma == "-":
                current_ma = None
            optical_rx_dbm = i["rxpw"]
            if optical_rx_dbm == "-":
                optical_rx_dbm = None
            optical_tx_dbm = i["txpw"]
            if optical_tx_dbm == "-":
                optical_tx_dbm = None
            r.append(
                {
                    "interface": i["port"],
                    "temp_c": temp_c,
                    "voltage_v": voltage_v,
                    "current_ma": current_ma,
                    "optical_rx_dbm": optical_rx_dbm,
                    "optical_tx_dbm": optical_tx_dbm,
                }
            )
        return r
