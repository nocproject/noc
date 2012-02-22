# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_copper_tdr_diag
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
import time
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetCopperTDRDiag


class Script(NOCScript):
    name = "Cisco.IOS.get_copper_tdr_diag"
    implements = [IGetCopperTDRDiag]
    rx_link = re.compile(r"^(?P<interface>\S+)\s+(auto|10M|100M|1000M)\s+Pair (?P<pair>A|B|C|D)\s+(?P<length>\d+)\s+\+/\- (?P<variance>\d+)\s+meters (?:Pair (?:A|B|C|D)|N/A)\s+(?P<status>Normal|Open|Short)")
    rx_pair = re.compile(r"^\s+Pair (?P<pair>A|B|C|D)\s+(?P<length>\d+)\s+\+/\- (?P<variance>\d+)\s+meters (?:Pair (?:A|B|C|D)|N/A)\s+(?P<status>Normal|Open|Short)")
    rx_link_nc = re.compile(r"^(?P<interface>\S+)\s+(auto|10M|100M|1000M)\s+Pair (?P<pair>A|B|C|D)\s+N/A\s+N/A\s+(?P<status>Not Completed)")
    rx_pair_nc = re.compile(r"^\s+Pair (?P<pair>A|B|C|D)\s+N/A\s+N/A\s+(?P<status>Not Completed)")

    def parce_pair(self, pair, status, distance=0, variance=None):
        if status == "Normal":
            st = 'T'
        elif status == "Open":
            st = 'O'
        elif status == "Short":
            st = 'S'
        elif status == "Not Completed":
            st = 'N'
        else:
            raise self.NotSupportedError()
        p = {"A": 1, "B": 2, "C": 3, "D": 4}.get(pair)
        if variance is not None:
            return {"pair": p, "status": st,
                "distance_cm": int(distance) * 100,
                "variance_cm": int(variance) * 100}
        else:
            return {"pair": p, "status": st,
                "distance_cm": int(distance) * 100}

    def execute(self, interface=None):
        r = []
        if interface is None:
            raise self.NotSupportedError()
        try:
            s = self.cli("test cable-diagnostics tdr interface %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        if s.startswith("% TDR test is not supported"):
            raise self.NotSupportedError()

        time.sleep(5)
        try:
            s = self.cli("show cable-diagnostics tdr interface %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        test = s.splitlines()
        i = 0
        while i < len(test):
            l = test[i]

            if l.startswith("% TDR test was never run on") \
            or l.startswith("% TDR test is not supported"):
                raise self.NotSupportedError()

            match = self.rx_link.search(l)
            if not match:
                match = self.rx_link_nc.search(l)

            if match:
                link = {
                    "interface": match.group("interface"),
                    "pairs": []
                }
                if match.group("status") != "Not Completed":
                    p = self.parce_pair(match.group("pair"),
                        match.group("status"), int(match.group("length")),
                        int(match.group("variance")))
                else:
                    p = self.parce_pair(match.group("pair"),
                        match.group("status"), 0)
                link["pairs"].append(p)

                i += 1
                l = test[i]
                match = self.rx_pair.search(l)
                if not match:
                    match = self.rx_pair_nc.search(l)

                while match:
                    if match.group("status") != "Not Completed":
                        p = self.parce_pair(match.group("pair"),
                            match.group("status"), int(match.group("length")),
                            int(match.group("variance")))
                    else:
                        p = self.parce_pair(match.group("pair"),
                            match.group("status"), 0)

                    link["pairs"].append(p)

                    i += 1
                    if i == len(test):
                        break
                    l = test[i]
                    match = self.rx_pair.search(l)
                    if not match:
                        match = self.rx_pair_nc.search(l)

                r.append(link)
                i -= 1

            i += 1
        return r
