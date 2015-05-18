# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_dom_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDOMStatus


class Script(NOCScript):
    name = "HP.1910.get_dom_status"
    implements = [IGetDOMStatus]

    # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<temp_c>(\d+|N/A|N/S))\s+(?P<voltage_v>\S+)\s+(?P<current_ma>\S+)\s+(?P<optical_rx_dbm>\S+)\s+(?P<optical_tx_dbm>\S+)\s+(No|Yes|N/A|N/S)")

    def execute(self, interface=None):
        r = []
        if interface is not None:
            cmd = "display transceiver diagnosis interface %s"\
                % interface.replace('Ge ', 'GigabitEthernet ')
        else:
            cmd = "display transceiver diagnosis interface"
        v = self.cli(cmd)
        for l in v.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            temp_c = match.group("temp_c")
            if temp_c == "N/A" or temp_c == "N/S":
                temp_c = None
            voltage_v = match.group("voltage_v")
            if voltage_v == "N/A" or voltage_v == "N/S":
                voltage_v = None
            current_ma = match.group("current_ma")
            if current_ma == "N/A" or current_ma == "N/S":
                current_ma = None
            optical_rx_dbm = match.group("optical_rx_dbm")
            if optical_rx_dbm == "N/A" or optical_rx_dbm == "N/S":
                optical_rx_dbm = None
            optical_tx_dbm = match.group("optical_tx_dbm")
            if optical_tx_dbm == "N/A" or optical_tx_dbm == "N/S":
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
