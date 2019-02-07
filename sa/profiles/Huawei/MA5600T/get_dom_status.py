# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus


class Script(BaseScript):
    name = "Huawei.MA5600T.get_dom_status"
    interface = IGetDOMStatus

    splitter = re.compile("\s*-+\n")

    def execute_cli(self, interface=None, **kwargs):
        if not interface:
            interface = '0/0/0'
        self.cli("config")
        frame, slot, port = interface.split("/")
        self.cli("interface gpon %s/%s" % (frame, slot))  # Fix from cpes
        r = []
        v = self.cli("display port state all")
        for port in self.splitter.split(v):
            port = {line.rsplit(None, 1)[0].strip(): line.rsplit(None, 1)[1].strip()
                    for line in port.splitlines() if len(line.rsplit(None, 1)) == 2}
            if not port:
                continue
            if port["Port state"] == "Offline":
                self.logger.info("Port %s is offline mode" % port["Port state"])
                continue
            r += [{"interface": port["F/S/P"],
                   "temp_c": float(port["Temperature(C)"]),
                   "voltage_v": float(port["Supply Voltage(V)"]),
                   "current_ma": float(port["TX Bias current(mA)"]),
                   "optical_tx_dbm": float(port["TX power(dBm)"]),
                   "optical_laser_state": str(port["Laser state"])}]
        self.cli("quit")
        self.cli("quit")
        return r
