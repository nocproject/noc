# ---------------------------------------------------------------------
# HP.Aruba.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "HP.Aruba.get_portchannel"
    interface = IGetPortchannel

    always_prefer = "S"

    def execute_snmp(self):
        r = []

        def hex2bin(ports):
            bin = [
                "0000",
                "0001",
                "0010",
                "0011",
                "0100",
                "0101",
                "0110",
                "0111",
                "1000",
                "1001",
                "1010",
                "1011",
                "1100",
                "1101",
                "1110",
                "1111",
            ]
            ports = ["%02x" % ord(c) for c in ports]
            p = ""
            for c in ports:
                for i in range(len(c) - 1):
                    p += bin[int(c[i], 16)]
            return p

            for v in self.snmp.get_tables(
                [
                    "1.2.840.10006.300.43.1.1.1.1.6",
                    "1.2.840.10006.300.43.1.1.2.1.1",
                    "1.2.840.10006.300.43.1.1.1.1.5",
                ],
                bulk=True,
            ):
                oid = "1.3.6.1.2.1.31.1.1.1.1." + str(v[1])
                port = self.snmp.get(oid, cached=True)  # IF-MIB
                if not port:
                    oid = "1.3.6.1.2.1.2.2.1.2." + str(v[1])
                    port = self.snmp.get(oid, cached=True)
                s = hex2bin(v[2])
                members = []
                for i in range(len(s)):
                    if s[i] == "1":
                        oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                        iface = self.snmp.get(oid, cached=True)  # IF-MIB
                        if not iface:
                            oid = "1.3.6.1.2.1.2.2.1.2." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)
                        members.append(iface)

                r.append(
                    {
                        "interface": port,
                        # ?????? type detection
                        # 1.2.840.10006.300.43.1.1.1.1.5 is correct???????????
                        "type": "L" if v[3] == "1" else "S",
                        "members": members,
                    }
                )
            return r
