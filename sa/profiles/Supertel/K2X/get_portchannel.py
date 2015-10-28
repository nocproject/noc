# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Supertel.K2X.get_portchannel"
    interface = IGetPortchannel

    rx_lag = re.compile(
        r"^(?P<port>ch\d+)(\s+Active:\s+(?P<interfaces1>\S+)|)+"
        r"(\s+Inactive:\s+(?P<interfaces2>\S+)|\s+Non-candidate:\s+"
        r"(?P<interfaces3>\S+)|)$",
        re.MULTILINE)

    rx_ifaces = re.compile(
        r"^g\((?P<ifaces>\S+)\)",
        re.MULTILINE)

    rx_lacp = re.compile(
        r"^\s+MAC Address:",
        re.MULTILINE)

    def execute(self):
        r = []
        """
        # Try SNMP first
        #
        # Detect only active links
        #
        if self.has_snmp():
            try:
                for v in self.snmp.get_tables([
                        "1.2.840.10006.300.43.1.1.1.1.6",
                        "1.2.840.10006.300.43.1.1.2.1.1",
                        "1.2.840.10006.300.43.1.1.1.1.5"],
                        bulk=True):
                    oid = "1.3.6.1.2.1.31.1.1.1.1." + v[1]
                    port = self.snmp.get(oid, cached=True)  # IF-MIB
                    s = self.hex_to_bin(v[2])
                    members = []
                    for i in range(len(s)):
                        if s[i] == '1':
                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)  # IF-MIB
                            members.append(iface)

                    if members:
                        r.append({
                            "interface": port,
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
            port = match.group("port")
            memb = []
            for members in [match.group("interfaces1"),
                            match.group("interfaces2"),
                            match.group("interfaces3")]:
                if members:
                    ifaces = self.rx_ifaces.search(members)
                    if ifaces:
                        ifaces = ifaces.group("ifaces").split(',')
                        for iface in ifaces:
                            if '-' in iface:
                                R = iface.split('-')
                                for i in range(int(R[0]), int(R[1]) + 1):
                                    memb += ['g' + str(i)]
                            else:
                                memb += ['g' + iface]
                    else:
                        memb += [members]
            lacp = self.cli("show lacp port-channel %s" % port[2:])
            match_ = self.rx_lacp.search(lacp)
            if match_:
                l_type = "L"
            else:
                l_type = "S"
            r += [{
                "interface": port,
                "type": l_type,
                "members": memb,
                }]
        return r
