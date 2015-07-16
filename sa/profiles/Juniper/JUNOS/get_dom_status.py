# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_dom_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus


class Script(NOCScript):
    name = "Juniper.JUNOS.get_dom_status"
    implements = [IGetDOMStatus]

    rx_phy_split = re.compile(r"^Physical interface:\s+", re.MULTILINE)
    rx_phy_name = re.compile(r"^(?P<ifname>\S+)")
    rx_temp = re.compile(
        r"Module temperature\s+:\s+(?P<temp>\S+) degrees")
    rx_bias = re.compile(r"Laser bias current\s+:\s+(?P<bias>\S+) mA")
    rx_tx_dbm = re.compile(
        r"Laser output power\s+:\s+\S+ mW / (?P<tx_dbm>\S+) dBm")
    rx_rx_dbm = re.compile(
        r"Laser rx power\s+:\s+\S+ mW / (?P<rx_dbm>\S+) dBm")

    def execute(self, interface=None):
        r = []
        v = self.cli("show interfaces diagnostics optics")
        for I in self.rx_phy_split.split(v)[1:]:
            name = self.re_search(self.rx_phy_name, I).group("ifname")
            temp_c = self.re_search(self.rx_temp, I).group("temp")
            voltage_v = 0
            current_ma = self.re_search(self.rx_bias, I).group("bias")
            optical_tx_dbm = self.re_search(self.rx_tx_dbm, I).group("tx_dbm")
            optical_rx_dbm = self.re_search(self.rx_rx_dbm, I).group("rx_dbm")
            r += [{
                "interface": name,
                "temp_c": temp_c,
                "voltage_v": voltage_v,
                "current_ma": current_ma,
                "optical_rx_dbm": optical_rx_dbm,
                "optical_tx_dbm": optical_tx_dbm
            }]
        return r
