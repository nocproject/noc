# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_copper_tdr_diag
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcoppertdrdiag import IGetCopperTDRDiag


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_copper_tdr_diag"
    interface = IGetCopperTDRDiag

    rx_link = re.compile(
        r"pairA:?\s+(?P<status_p1>\w+)(\s+(?P<len_p1>\d+\.\d+|N\/A)\s+(?P<len_fault_p1>\d+\.\d+|N\/A))?"
        r".*pairB:?\s+(?P<status_p2>\w+)(\s+(?P<len_p2>\d+\.\d+|N\/A)\s+(?P<len_fault_p2>\d+\.\d+|N\/A))?"
        r".*pairC:?\s+(?P<status_p3>\w+)(\s+(?P<len_p3>\d+\.\d+|N\/A)\s+(?P<len_fault_p3>\d+\.\d+|N\/A))?"
        r".*pairD:?\s+(?P<status_p4>\w+)(\s+(?P<len_p4>\d+\.\d+|N\/A)\s+(?P<len_fault_p4>\d+\.\d+|N\/A))?",
        re.MULTILINE | re.DOTALL,
    )

    def convert_to_cm(self, distance):
        try:
            return float(distance) * 100
        except (ValueError, TypeError):
            pass
        return 0

    def convert_status(self, zstatus):
        return {"Ok": "T", "Open": "O", "Short": "S"}[zstatus]

    def execute(self, interface):
        r = []
        s = self.cli("cable-diagnostics %s" % interface)
        for match in self.rx_link.finditer(s):
            r += [
                {
                    "interface": interface,
                    "pairs": [
                        {
                            "pair": 1,
                            "status": self.convert_status(match.group("status_p1")),
                            "distance_cm": self.convert_to_cm(match.group("len_p1")),
                            "distance_fault_cm": self.convert_to_cm(match.group("len_fault_p1")),
                        },
                        {
                            "pair": 2,
                            "status": self.convert_status(match.group("status_p2")),
                            "distance_cm": self.convert_to_cm(match.group("len_p2")),
                            "distance_fault_cm": self.convert_to_cm(match.group("len_fault_p2")),
                        },
                        {
                            "pair": 3,
                            "status": self.convert_status(match.group("status_p3")),
                            "distance_cm": self.convert_to_cm(match.group("len_p3")),
                            "distance_fault_cm": self.convert_to_cm(match.group("len_fault_p3")),
                        },
                        {
                            "pair": 4,
                            "status": self.convert_status(match.group("status_p4")),
                            "distance_cm": self.convert_to_cm(match.group("len_p4")),
                            "distance_fault_cm": self.convert_to_cm(match.group("len_fault_p4")),
                        },
                    ],
                }
            ]

        return r
