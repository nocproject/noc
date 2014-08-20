# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_copper_tdr_diag
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetCopperTDRDiag
from noc.sa.profiles.DLink.DGS3100 import DGS3100


class Script(NOCScript):
    name = "DLink.DGS3100.get_copper_tdr_diag"
    implements = [IGetCopperTDRDiag]
    rx_link_ok = re.compile(
        r"^\s*(?P<interface>\d+([\/:]\d+)?)\s+"
        r"(FE|GE|10GE|1000BASE\-T|10GBASE-R)\s+Link Up\s+"
        r"OK\s+(?P<length>\d+)", re.IGNORECASE
    )
    rx_link_nc = re.compile(
        r"^\s*(?P<interface>\d+([\/:]\d+)?)\s+"
        r"(FE|GE|10GE|1000BASE\-T|10GBASE-R)\s+Link Down\s+"
        r"(?:No Cable)(\s+\-)?", re.IGNORECASE
    )
    rx_link_pr = re.compile(
        r"^\s*(?P<interface>\d+([\/:]\d+)?)\s+"
        r"(FE|GE|10GE|1000BASE\-T|10GBASE-R)\s+Link (?:Up|Down)\s+"
        r"Pair\s*(?P<num>\d+)\s+(?P<status>OK|Open|Short)\s+at\s+"
        r"(?P<length>\d+)\s*M\s+-", re.IGNORECASE
    )
    rx_pair = re.compile(
        r"^\s+Pair\s*(?P<num>\d+)\s+(?P<status>OK|Open|Short|Not Support)"
        r"(\s+at\s+(?P<length>\d+)\s*M)?", re.IGNORECASE
    )
    variance = 0

    def parce_pair(self, pair, status, distance=None):
        pair = int(pair)
        if status == "OK":
            st = 'T'
        elif status == "Open":
            st = 'O'
        elif status == "Short":
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
        if self.match_version(DGS3100, version__lte="3.60.28"):
            raise self.NotSupportedError()
        self.variance = 100
        if interface is None:
            interface = "all"
        try:
            s = self.cli("cable_diag ports %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        test = s.splitlines()
        i = 0
        while i < len(test):
            l = test[i]

            match = self.rx_link_ok.search(l)
            if match:
                length = int(match.group("length")) * 100
                r += [{
                    "interface": match.group("interface"),
                    "pairs": [
                        {"pair": 1, "status": "T",
                            "distance_cm": length,
                            "variance_cm": self.variance},
                        {"pair": 2, "status": "T",
                            "distance_cm": length,
                            "variance_cm": self.variance},
                        {"pair": 3, "status": "T",
                            "distance_cm": length,
                            "variance_cm": self.variance},
                        {"pair": 4, "status": "T",
                            "distance_cm": length,
                            "variance_cm": self.variance}
                    ]
                }]

            match = self.rx_link_nc.search(l)
            if match:
                r += [{
                    "interface": match.group("interface"),
                    "pairs": [
                        {"pair": 1, "status": "N", "distance_cm": 0},
                        {"pair": 2, "status": "N", "distance_cm": 0},
                        {"pair": 3, "status": "N", "distance_cm": 0},
                        {"pair": 4, "status": "N", "distance_cm": 0}
                    ]
                }]

            match = self.rx_link_pr.search(l)
            if match:
                pair = int(match.group("num"))
                status = match.group("status")
                distance = int(match.group("length"))
                link = {
                    "interface": match.group("interface"),
                    "pairs": []
                }
                p = self.parce_pair(pair, status, distance)
                link["pairs"].append(p)

                i += 1
                l = test[i]

                match = self.rx_pair.search(l)
                while match and i < len(test):
                    pair = int(match.group("num"))
                    status = match.group("status")
                    if match.group("length"):
                        distance = int(match.group("length"))
                        p = self.parce_pair(pair, status, distance)
                    else:
                        p = self.parce_pair(pair, status)
                    link["pairs"].append(p)

                    i += 1
                    l = test[i]
                    match = self.rx_pair.search(l)

                r.append(link)
                i -= 1

            i += 1
        return r
