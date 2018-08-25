# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MA4000.get_dom_status"
    interface = IGetDOMStatus

    def execute(self, interface=None):
        r = []
        if interface is None:
            interface = "all"
        c = self.cli("show sfp front-port %s" % interface)
        t = parse_table(c, allow_wrap=True)
        for i in t:
            port = ' '.join(i[0].split())
            if not port.startswith("front-port"):
                continue
            temp_c = i[1]
            if temp_c in ["N/A", "N/S"]:
                temp_c = None
            voltage_v = i[2]
            if voltage_v in ["N/A", "N/S"]:
                voltage_v = None
            current_ma = i[3]
            if current_ma in ["N/A", "N/S"]:
                current_ma = None
            optical_rx_dbm = i[4]
            if optical_rx_dbm in ["N/A", "N/S"]:
                optical_rx_dbm = None
            optical_tx_dbm = i[5]
            if optical_tx_dbm in ["N/A", "N/S"]:
                optical_tx_dbm = None
            r += [{
                "interface": port,
                "temp_c": temp_c,
                "voltage_v": voltage_v,
                "current_ma": current_ma,
                "optical_rx_dbm": optical_rx_dbm,
                "optical_tx_dbm": optical_tx_dbm
            }]
        return r
