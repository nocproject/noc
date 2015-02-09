# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_copper_tdr_diag
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
    name = "Zyxel.ZyNOS.get_copper_tdr_diag"
    implements = [IGetCopperTDRDiag]

    rx_link = re.compile(r"^port (?P<interface>fe\d+): cable\s+(?:\S+)\s+"
                        "\(2 pairs.*\).\s+pair A (?P<status_p1>\S+), "
                        "length (?P<len_p1>\d+) metres.\s+pair B "
                        "(?P<status_p2>\S+), length (?P<len_p2>\d+) metres$",
                        re.MULTILINE | re.DOTALL)

    def execute(self, interface=None):
        r = []
        with self.zynos_mode():
            s = self.cli("bcm cablediag %s" % interface)
        for match in self.rx_link.finditer(s):
            r += [{"interface": match.group("interface"),
                    "pairs": [{
                        "pair": 1,
                        "status": {"Ok": "T", "Open": "O", "Short": "S"}
                            [match.group("status_p1")],
                        "distance_cm": int(match.group("len_p1")) * 100,
                    }, {
                        "pair": 2,
                        "status": {"Ok": "T", "Open": "O", "Short": "S"}
                            [match.group("status_p2")],
                        "distance_cm": int(match.group("len_p2")) * 100,
                    }, {
                        "pair": 3,
                        "status": "N",
                        "distance_cm": 0,
                    }, {
                        "pair": 4,
                        "status": "N",
                        "distance_cm": 0,
                    }]
            }]

        return r
