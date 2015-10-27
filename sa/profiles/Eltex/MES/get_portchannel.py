# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
    name = "Eltex.MES.get_portchannel"
    implements = [IGetPortchannel]

    rx_lag = re.compile(
        r"^(?P<port>Po\d+)\s+(?P<type1>\S+):\s+(?P<interfaces1>\S+)+(\s+(?P<type2>\S+):\s+(?P<interfaces2>\S+)$|$)",
        re.MULTILINE)

    rx_lacp = re.compile(
        r"^\s+Attached Lag id:$",
        re.MULTILINE)

    def execute(self):
        r = []
        """ Detect only active links
        # Try SNMP first
        if self.has_snmp():
            try:
                for v in self.snmp.get_tables(
                    ["1.2.840.10006.300.43.1.1.1.1.6",
                    "1.2.840.10006.300.43.1.1.2.1.1",
                    "1.2.840.10006.300.43.1.1.1.1.5"], bulk=True):
                    oid = "1.3.6.1.2.1.31.1.1.1.1." + v[1]
                    port = self.snmp.get(oid, cached=True)  # IF-MIB
                    s = self.hex_to_bin(v[2])
                    print port
                    print s
                    members = []
                    for i in range(len(s)):
                        if s[i] == '1':
                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)  # IF-MIB
                            members.append(iface)

                    if members:
                        r.append({
                            "interface": port,
                            # ?????? type detection
                            # 1.2.840.10006.300.43.1.1.1.1.5 is correct???????????
                            "type": "L" if v[3] == '1' else "S",
                            "members": members,
                            })
                return r
            except self.snmp.TimeOutError:
                pass
            """

        # Fallback to CLI
        cmd = self.cli("show interfaces port-channel")
        for match in self.rx_lag.finditer(cmd):
            members = match.group("interfaces1").split(',')
            memb = []
            for iface in members:
                if '-' in iface:
                    mas = iface.split('/')
                    R = mas[2].split('-')
                    for i in range(int(R[0]), int(R[1]) + 1):
                        memb += [mas[0] + '/' + mas[1] + '/' + str(i)]
                else:
                    memb += [iface]
            members2 = match.group("interfaces2")
            if members2:
                members2 = members2.split(',')
                for iface in members2:
                    if '-' in iface:
                        mas = iface.split('/')
                        R = mas[2].split('-')
                        for i in range(int(R[0]), int(R[1]) + 1):
                            memb += [mas[0] + '/' + mas[1] + '/' + str(i)]
                    else:
                        memb += [iface]
            lacp = self.cli("show lacp Port-Channel")
            match_ = self.rx_lacp.search(lacp)
            if match_:
                l_type = "L"
            else:
                l_type = "S"
            r += [{
                "interface": match.group("port").lower(),
#                "interface": match.group("port"),
                "type": l_type,
                "members": memb,
                }]
        return r
