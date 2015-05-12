# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_copper_tdr_diag
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetCopperTDRDiag


class Script(NOCScript):
    name = "Supertel.K2X.get_copper_tdr_diag"
    implements = [IGetCopperTDRDiag]

    variance = 100

    rx_tdr = re.compile(
        r"\s*(?P<interface>g\d+)\s+"
        r"(?P<status>(OK|Open cable|Short cable|No cable))\s+"
        r"((?P<length>\d+)\s+\S+\s+\S+\s*|)$",
        re.MULTILINE | re.IGNORECASE)

    def execute(self, interface=None):
        r = []
        if interface is None:
            for i in self.scripts.get_interface_status():
                self.cli("test copper-port tdr %s" % i["interface"])
            cmd = "show copper-ports tdr"
        else:
            self.cli("test copper-port tdr %s" % interface)
            cmd = "show copper-ports tdr %s" % interface

        status = {
            "OK": 'T',
            "Open cable": 'O',
            "Short cable": 'S',
            "No cable": 'N'
            }

        for match in self.rx_tdr.finditer(self.cli(cmd)):
            status_ = match.group("status")
            if match.group("length"):
                length = int(match.group("length")) * 100
            else:
                length = 0
            pairs = []
            for pair in [1, 2, 3, 4]:
                pairs.append({
                    "pair": pair,
                    "status": status[status_],
                    "distance_cm": int(length),
                    "variance_cm": self.variance
                    })
            r.append({
                "interface": match.group("interface"),
                "pairs": pairs
                })
        return r
