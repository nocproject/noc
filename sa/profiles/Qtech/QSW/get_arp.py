# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetARP


class Script(noc.sa.script.Script):
    name = "Qtech.QSW.get_arp"
    implements = [IGetARP]
    cache = True

    rx_line = re.compile(
        r"^(?P<ip>\S+)\s+(?P<mac>\S+)\s+\d+\s+(?P<interface>\S+)\s+(?P<type>\S+)\s+(?P<status>\S+)",
        re.MULTILINE)

    rx_line1 = re.compile(
        r"^(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s+(?P<port>\S+)\s+(?P<flag>Dynamic|Static)\s+(?P<age>\d+)",
        re.MULTILINE)

    def execute(self):
        r = []
        # Try SNMP first
        """
        # Working but give interfase name "system"!!!

        if self.snmp and self.access_profile.snmp_ro:
            try:
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.4.22.1.1", "1.3.6.1.2.1.4.22.1.2",
                    "1.3.6.1.2.1.4.22.1.3"], bulk=True):
                    iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[1],
                        cached=True)  # IF-MIB
                    mac = ":".join(["%02x" % ord(c) for c in v[2]])
                    ip = ["%02x" % ord(c) for c in v[3]]
                    ip = ".".join(str(int(c, 16)) for c in ip)
                    r.append({"ip": ip,
                            "mac": mac,
                            "interface": iface,
                            })
                return r
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        try:
            v = self.cli("show arp all", cached=True)
            rx_iter = self.rx_line
        except self.CLISyntaxError:
            v = self.cli("show arp", cached=True)
            rx_iter = self.rx_line1

        for match in rx_iter.finditer(v):
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r.append({
                    "ip": match.group("ip"),
                    "mac": None,
                    "interface": None
                    })
            else:
                r.append({
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("port")
                    })
        return r
