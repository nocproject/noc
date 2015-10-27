# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP


class Script(NOCScript):
    name = "Supertel.K2X.get_arp"
    implements = [IGetARP]
    cache = True

    rx_line = re.compile(
        r"^(VLAN\s+\d+|)\s+(?P<interface>\S+)\s+(?P<ip>\S+)\s+"
        r"(?P<mac>\S+)\s+(Dynamic|Static)\s*$",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        r = []
        """
        # Try SNMP first
        #
        # Some time return vlan ID, not interface name!!!
        #
        if self.has_snmp():
            try:
                for v in self.snmp.get_tables(["1.3.6.1.2.1.4.22.1.1",
                                               "1.3.6.1.2.1.4.22.1.2",
                                               "1.3.6.1.2.1.4.22.1.3"],
                                              bulk=True):
                    iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[1],
                                          cached=True)
                    mac = ":".join(["%02x" % ord(c) for c in v[2]])
                    ip = ["%02x" % ord(c) for c in v[3]]
                    ip = ".".join(str(int(c, 16)) for c in ip)
                    r.append({
                        "ip": ip,
                        "mac": mac,
                        "interface": iface,
                        })
                return r
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        for match in self.rx_line.finditer(self.cli("show arp", cached=True)):
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
                    "interface": match.group("interface")
                    })
        return r
