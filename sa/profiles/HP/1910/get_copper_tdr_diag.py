# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_copper_tdr_diag
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetCopperTDRDiag


class Script(BaseScript):
    name = "HP.1910.get_copper_tdr_diag"
    interface = IGetCopperTDRDiag
    TIMEOUT = 600

    rx_diag = re.compile(
        r"^Cable status: (?P<status>\S+), (?P<length>\d+) metres")
    variance = 100

    def parce_pair(self, pair, status, distance=None):
        pair = int(pair)
        if status == "normal":
            st = 'T'
        elif status == "abnormal(open)":
            st = 'O'
        elif status == "abnormal(short)":
            st = 'S'
        elif status == "abnormal(unknown)":
            st = 'N'
        else:
            raise self.NotSupportedError()
        return {"pair": pair, "status": st, "distance_cm": int(distance),
            "variance_cm": self.variance}

    def execute(self, interface=None):
        r = []
        with self.configure():
            if interface is None:
                interface_status = {}
                diag = ''
                for iface in self.scripts.get_interface_status():
                    diag = self.cli("interface %s" % iface['interface'].replace('Ge ', 'GigabitEthernet '))
                    diag = self.cli("virtual-cable-test")
                    match = self.rx_diag.search(diag)
                    if match:
                        status = match.group("status")
                        length = int(match.group("length")) * 100
                        pairs = []
                        for i in [1, 2, 3, 4]:
                            pairs.append(self.parce_pair(i, status, length))
                        r.append({
                            "interface": iface['interface'],
                            "pairs": pairs
                            })
            else:
                diag = self.cli("interface %s" % interface.replace('Ge ', 'GigabitEthernet '))
                diag = self.cli("virtual-cable-test")
                match = self.rx_diag.search(diag)
                if match:
                    status = match.group("status")
                    length = int(match.group("length")) * 100
                    pairs = []
                    for i in [1, 2, 3, 4]:
                        pairs.append(self.parce_pair(i, status, length))
                    r.append({
                        "interface": interface,
                        "pairs": pairs
                        })
        return r
