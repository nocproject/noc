# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus
from noc.lib.convert import mw2dbm


class Script(BaseScript):
    name = "SKS.SKS.get_dom_status"
    interface = IGetDOMStatus

    rx_port = re.compile(
        r"^\s+(?P<port>(?:gi|te)\d+\S+)\s+(?P<temp>\S+)\s+(?P<volt>\S+)\s+"
        r"(?P<bias>\S+)\s+(?P<txpw>\S+)\s+(?P<rxpw>\S+)\s+(?P<los>\S+)\s*$",
        re.MULTILINE)

    def parse_value(self, m, g):
        v = m.group(g)
        if v in ["N/A", "N/S"]:
            v = None
        elif g in["rxpw", "txpw"]:
            v = round(mw2dbm(v), 2)
        return v

    def execute(self, interface=None):
        cmd = "show fiber-ports optical-transceiver detailed"
        if interface is not None:
            cmd += " interface %s" % interface
        r = []
        try:
            v = self.cli(cmd)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_port.finditer(v):
            i = {
                "interface": match.group("port"),
                "temp_c": self.parse_value(match, "temp"),
                "voltage_v": self.parse_value(match, "volt"),
                "current_ma": self.parse_value(match, "bias"),
                "optical_rx_dbm": self.parse_value(match, "rxpw"),
                "optical_tx_dbm": self.parse_value(match, "txpw")
            }
            if (i["temp_c"] is None) and (i["voltage_v"] is None) \
            and (i["current_ma"] is None) and (i["optical_rx_dbm"] is None) \
            and (i["optical_tx_dbm"] is None):
                continue
            r += [i]
        return r
