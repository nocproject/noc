# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_dom_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDOMStatus


class Script(NOCScript):
    name = "DLink.DxS.get_dom_status"
    implements = [IGetDOMStatus]

    rx_port = re.compile(r"^\s+(?P<port>\d+\S*)\s+(?P<temp>\S+)\s+(?P<volt>\S+)\s+(?P<bias>\S+)\s+(?P<txpw>\S+)\s+(?P<rxpw>\S+)\s*$", re.MULTILINE)

    def parse_ports(self, s):
        match = self.rx_port.search(s)
        if match:
            port = match.group("port")
            obj = {
                "port": port,
                "temp": match.group("temp"),
                "volt": match.group("volt"),
                "bias": match.group("bias"),
                "txpw": match.group("txpw"),
                "rxpw": match.group("rxpw")
            }
            return port, obj, s[match.end():]
        else:
            return None

    def execute(self, interface=None):
        cmd = "show ddm ports status"
        if interface is not None:
            cmd = "show ddm ports %s status" % interface
        try:
            ports = self.cli_object_stream(
                cmd, parser=self.parse_ports, cmd_next="n", cmd_stop="q")
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
            r.append({
                "interface": i["port"],
                "temp_c": temp_c,
                "voltage_v": voltage_v,
                "current_ma": current_ma,
                "optical_rx_dbm": optical_rx_dbm,
                "optical_tx_dbm": optical_tx_dbm
            })
        return r
