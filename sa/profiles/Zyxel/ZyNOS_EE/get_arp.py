# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Zyxel.ZyNOS_EE.get_arp"
    interface = IGetARP

    rx_arp = re.compile(
        r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+\S+\s+\d+\s+(?P<mac>\S+)\s+\d+\s+(?P<interface>\S+)",
        re.MULTILINE)

    def execute(self):
        r = []
        # Try SNMP first
        if self.has_snmp():
            try:
                mac_ip = {}
                for mac, ip in self.snmp.join_tables("1.3.6.1.2.1.4.22.1.2",
                                                     "1.3.6.1.2.1.4.22.1.3", cached=True):  # IP-MIB
                    mac = ":".join(["%02x" % ord(c) for c in mac])
                    ip = ["%02x" % ord(c) for c in ip]
                    mac_ip[mac] = ".".join(str(int(c, 16)) for c in ip)
                for i, mac in self.snmp.join_tables("1.3.6.1.2.1.4.22.1.1",
                                                    "1.3.6.1.2.1.4.22.1.2", cached=True):  # IP-MIB
                    mac = ":".join(["%02x" % ord(c) for c in mac])
                    interface = self.snmp.get("1.3.6.1.2.1.2.2.1.1." + i,
                        cached=True)  # IF-MIB
                    try:
                        r.append({"ip": mac_ip[mac],
                            "mac": mac,
                            "interface": interface,
                            })
                    except KeyError:
                        pass
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        arp = self.cli("ip arp status")
        for match in self.rx_arp.finditer(arp):
            r.append({
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
                })
        return r
