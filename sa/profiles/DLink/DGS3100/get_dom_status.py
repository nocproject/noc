# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDOMStatus
import re


class Script(NOCScript):
    name = "DLink.DGS3100.get_dom_status"
    implements = [IGetDOMStatus]
    rx_line = re.compile(r"^\s+(?P<interface>\d+:\d+)\s+(?P<temp_c>\S+)\s+(?P<voltage_v>\S+)\s+(?P<current_ma>\S+)\s+(?P<optical_tx_dbm>\S+)\s+(?P<optical_rx_dbm>\S+)\s+\S+", re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
        if interface is None:
            interface = "9-24"
        try:
            s = self.cli("show optical-transceiver %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_line.finditer(s):
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
