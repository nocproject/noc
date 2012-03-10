# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_copper_tdr_diag
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetCopperTDRDiag


class Script(NOCScript):
    name = "Eltex.MES.get_copper_tdr_diag"
    implements = [IGetCopperTDRDiag]
    rx_diag = re.compile(
        r"Cable on port\s+(?P<interface>\S+)\s+(?P<status>(is open|has short circuit))\s+at\s+(?P<length>\d+)\s+m",
        re.IGNORECASE)
    rx_diag_good = re.compile(
        r"Cable on port\s+(?P<interface>\S+)\s+(?P<status>is good)",
        re.IGNORECASE)
    variance = 100

    def parce_pair(self, pair, status, distance=None):
        pair = int(pair)
        if status == "is good":
            st = 'T'
        elif status == "is open":
            st = 'O'
        elif status == "has short circuit":
            st = 'S'
        elif status == "Not Support":
            st = 'N'
        else:
            raise self.NotSupportedError()
        if distance is not None:
            return {"pair": pair, "status": st, "distance_cm": int(distance),
            "variance_cm": self.variance}
        else:
            return {"pair": pair, "status": st, "distance_cm": 0}

    def execute(self, interface=None):
        r = []
        if interface is None:
            interface_status = {}
            diag = ''
            for s in self.scripts.get_interface_status():
                interface_status[s["interface"]] = s["status"]
                diag = diag + self.cli(
                    "test cable-diagnostics tdr interface %s" % s["interface"])
        else:
            diag = self.cli(
                    "test cable-diagnostics tdr interface %s" % interface)

        for l in diag.split('\n'):
            match = self.rx_diag.search(l)
            if match:
                status = match.group("status")
                length = int(match.group("length")) * 100
                pairs = []
                for i in [1, 2, 3, 4]:
                    pairs.append(self.parce_pair(i, status, length))
                r.append({
                    "interface": match.group("interface"),
                    "pairs": pairs
                    })
            match = self.rx_diag_good.search(l)
            if match:
                status = match.group("status")
                length = 0
                pairs = []
                for i in [1, 2, 3, 4]:
                    pairs.append(self.parce_pair(i, status, length))
                r.append({
                    "interface": match.group("interface"),
                    "pairs": pairs
                    })
        return r
