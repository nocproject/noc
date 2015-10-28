# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "HP.1905.get_portchannel"
    interface = IGetPortchannel

    def execute(self):
        r = []
        # Try SNMP first
        if self.has_snmp():
            def hex2bin(ports):
                bin = [
                    '0000', '0001', '0010', '0011',
                    '0100', '0101', '0110', '0111',
                    '1000', '1001', '1010', '1011',
                    '1100', '1101', '1110', '1111',
                    ]
                ports = ["%02x" % ord(c) for c in ports]
                p = ''
                for c in ports:
                    for i in range(len(c)):
                        p += bin[int(c[i], 16)]
                return p
            try:
                for v in self.snmp.get_tables(
                    ["1.2.840.10006.300.43.1.1.1.1.6",
                    "1.2.840.10006.300.43.1.1.2.1.1",
                    "1.2.840.10006.300.43.1.1.1.1.5"], bulk=True):
                    oid = "1.3.6.1.2.1.31.1.1.1.1." + v[1]
                    port = self.snmp.get(oid, cached=True)  # IF-MIB
                    if not port:
                        oid = "1.3.6.1.2.1.2.2.1.2." + v[1]
                        port = self.snmp.get(oid, cached=True)
#                    s = self.hex_to_bin(v[2])
                    s = hex2bin(v[2])
                    members = []
                    for i in range(len(s)):
                        if s[i] == '1':
                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)  # IF-MIB
                            if not iface:
                                oid = "1.3.6.1.2.1.2.2.1.2." + str(i + 1)
                                iface = self.snmp.get(oid, cached=True)
                            members.append(iface)

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

        # Fallback to CLI
        raise Exception("Not implemented")
