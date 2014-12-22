# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.NXOS.get_dom_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
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
    name = "Cisco.NXOS.get_dom_status"
    implements = [IGetDOMStatus]
    rx_xcvr = re.compile(r"(?P<interface>Ethernet\S+)\n.+\s+Temperature"
        r"\s+(?P<temp_c>\S+).+\n\s+Voltage\s+(?P<voltage_v>\S+).+\n\s+"
        r"Current\s+(?P<current_ma>\S+).+\n\s+Tx Power\s+"
        r"(?P<optical_tx_dbm>\S+).+\n\s+Rx Power\s+(?P<optical_rx_dbm>\S+)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self, interface=None):
        cmd = "show interface transceiver details | no-more"
        if interface is not None:
            cmd = "show interface %s transceiver details" % interface
        try:
            v = self.cli(cmd)
        except self.CLISyntaxError:
            return []

        r = []
        for i in v.replace("Ethernet","\n===\nEthernet").split("\n===\n"):
            match = self.rx_xcvr.match(i)
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
            r += [{
                "interface": match.group("interface"),
                "temp_c": temp_c,
                "voltage_v": voltage_v,
                "current_ma": current_ma,
                "optical_rx_dbm": optical_rx_dbm,
                "optical_tx_dbm": optical_tx_dbm
            }]
        return r
