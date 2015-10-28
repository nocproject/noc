# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_dom_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetDOMStatus


class Script(BaseScript):
    name = "Supertel.K2X.get_dom_status"
    interface = IGetDOMStatus

    rx_line = re.compile(
        r"^\s*(?P<interface>g\d+)\s+(?P<temp_c>(\d+|N/A|N/S))\s+"
        r"(?P<voltage_v>\S+)\s+(?P<current_ma>\S+)\s+"
        r"(?P<optical_tx_dbm>\S+)\s+(?P<optical_rx_dbm>\S+)\s+"
        r"(No|Yes|N/A|N/S)")

    def execute(self, interface=None):
        cmd = "show fiber-ports optical-transceiver"
        if interface is not None:
            cmd = "show fiber-ports optical-transceiver %s" % interface
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
