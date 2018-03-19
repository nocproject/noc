# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus


class Script(BaseScript):
    name = "Juniper.JUNOS.get_dom_status"
    interface = IGetDOMStatus

    rx_phy_split = re.compile(r"^Physical interface:\s+", re.MULTILINE)
    rx_phy_name = re.compile(r"^(?P<ifname>\S+)")
    rx_temp = re.compile(
        r"Module temperature\s+:\s+(?P<temp>\S+) degrees")
    rx_volt = re.compile(
        r"Module voltage\s+:\s+(?P<volt>\S+) V")
    rx_bias = re.compile(r"Laser bias current\s+:\s+(?P<bias>\S+) mA")
    rx_tx_dbm = re.compile(
        r"Laser output power\s+:\s+\S+ mW / (?P<tx_dbm>\S+) dBm")
    rx_rx_dbm = re.compile(
        r"(?:Laser rx|Receiver signal average optical) power\s+:\s+\S+ mW "
        r"/ (?P<rx_dbm>\S+) dBm")

    def execute(self, interface=None):
        r = []
        v = self.cli("show interfaces diagnostics optics")
        for I in self.rx_phy_split.split(v)[1:]:
            name = self.rx_phy_name.search(I).group("ifname")
            match = self.rx_temp.search(I)
            if match:
                temp_c = match.group("temp")
            else:
                temp_c = 0
            match = self.rx_volt.search(I)
            if match:
                voltage_v = match.group("volt")
            else:
                voltage_v = 0
            current_ma = self.rx_bias.search(I).group("bias")
            optical_tx_dbm = self.rx_tx_dbm.search(I).group("tx_dbm")
            optical_rx_dbm = self.rx_rx_dbm.search(I).group("rx_dbm")
            r += [{
                "interface": name,
                "temp_c": temp_c,
                "voltage_v": voltage_v,
                "current_ma": current_ma,
                "optical_rx_dbm": optical_rx_dbm,
                "optical_tx_dbm": optical_tx_dbm
            }]
        return r
