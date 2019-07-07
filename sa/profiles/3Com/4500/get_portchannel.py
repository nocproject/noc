# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# 3Com.4500.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "3Com.4500.get_portchannel"
    interface = IGetPortchannel

    rx_po = re.compile(r"^Aggregation Interface: Bridge-Aggregation(?P<port>\d+)$", re.MULTILINE)

    rx_type = re.compile(r"^Aggregation Mode: (?P<type>\S+)$", re.MULTILINE)

    rx_iface = re.compile(r"^\s+(?P<interface>\S+)\s+\S\s+\d+\s+\d\s+\S+$", re.MULTILINE)

    def execute_snmp(self):
        r = []
        for v in self.snmp.get_tables(
            [
                "1.2.840.10006.300.43.1.1.1.1.6",
                "1.2.840.10006.300.43.1.1.2.1.1",
                "1.2.840.10006.300.43.1.1.1.1.5",
            ]
        ):
            port = "Po" + v[1]
            s = self.hex_to_bin(v[2])
            members = []
            for i in range(len(s)):
                if s[i] == "1":
                    oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                    iface = self.snmp.get(oid, cached=True)  # IF-MIB
                    members.append(iface)

            r += [
                {
                    "interface": port,
                    # ?????? type detection
                    # 1.2.840.10006.300.43.1.1.1.1.5 is correct???????????
                    "type": "L" if v[3] == "1" else "S",
                    "members": members,
                }
            ]
        return r

    def execute_cli(self):
        r = []
        data = self.cli("display link-aggregation verbose").split("\n")
        L = len(data) - 1
        i = 0
        while i < L:
            ll = data[i]
            match = self.rx_po.search(ll)
            while not match:
                if i == L:
                    break
                i += 1
                ll = data[i]
                match = self.rx_po.search(ll)
            if i == L:
                break
            port = "Po" + match.group("port")
            i += 1
            ll = data[i]
            match = self.rx_type.search(ll)
            while not match:
                i += 1
                ll = data[i]
                match = self.rx_type.search(ll)
            typ = match.group("type")
            i += 1
            ll = data[i]
            match = self.rx_iface.search(ll)
            members = []
            while not match:
                i += 1
                ll = data[i]
                match = self.rx_iface.search(ll)
            while match:
                members.append(match.group("interface").replace("GE", "gi"))
                i += 1
                ll = data[i]
                match = self.rx_iface.search(ll)

            r += [{"interface": port, "type": "L" if typ == "Dynamic" else "S", "members": members}]

        return r
