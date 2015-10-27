# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetARP


class Script(noc.sa.script.Script):
    name = "Eltex.PON.get_arp"
    implements = [IGetARP]
    cache = True

    rx_line = re.compile(
        r"^\s*\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<interface>(\S+ \d+|\S+))"
        r"\s+\S+$", re.MULTILINE)

    def execute(self):
        r = []
        """
        # Try SNMP first
        if self.has_snmp():
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
        with self.profile.switch(self):
            arp = self.cli("show ip arp table\r")
        for match in self.rx_line.finditer(arp):
            mac = match.group("mac")
            if mac.lower() == "00:00:00:00:00:00":
                r.append({
                    "ip": match.group("ip"),
                    "mac": None,
                    "interface": None
                    })
            else:
                r.append({
                    "ip": match.group("ip"),
                    "mac": mac,
                    "interface": match.group("interface")
                    })
        return r
