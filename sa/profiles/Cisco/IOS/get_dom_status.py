# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_dom_status
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
    name = "Cisco.IOS.get_dom_status"
    implements = [IGetDOMStatus]
    rx_line = re.compile(r"^(?P<interface>\S+)\s+(?P<temp_c>\S+)\s+(?P<voltage_v>\S+)\s+(?P<current_ma>\S+)\s+(?P<optical_rx_dbm>\S+)\s+(?P<optical_tx_dbm>\S+)$")

    def execute(self, interface=None):
        cmd = "show interfaces transceiver | i /"
        if interface is not None:
            cmd = "show interfaces %s transceiver | i /" % interface
        try:
            v = self.cli(cmd)
        except self.CLISyntaxError:
            return []

        r = []
        for l in v.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            temp_c = match.group("temp_c")
            if temp_c == "N/A":
                temp_c = None
            voltage_v = match.group("voltage_v")
            if voltage_v == "N/A":
                voltage_v = None
            current_ma = match.group("current_ma")
            if current_ma == "N/A":
                current_ma = None
            optical_rx_dbm = match.group("optical_rx_dbm")
            if optical_rx_dbm == "N/A":
                optical_rx_dbm = None
            optical_tx_dbm = match.group("optical_tx_dbm")
            if optical_tx_dbm == "N/A":
                optical_tx_dbm = None
            r.append({
                "interface": match.group("interface"),
                "temp_c": temp_c,
                "voltage_v": voltage_v,
                "current_ma": current_ma,
                "optical_rx_dbm": optical_rx_dbm,
                "optical_tx_dbm": optical_tx_dbm
            })
        return r
