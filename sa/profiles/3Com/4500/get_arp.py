# ---------------------------------------------------------------------
# 3Com.4500.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "3Com.4500.get_arp"
    interface = IGetARP
    cache = True

    rx_line = re.compile(
        r"^(?P<ip>\S+)\s+(?P<mac>\S+)\s+\d+\s+(?P<interface>\S+)\s+\d+\s+\S$", re.MULTILINE
    )

    def execute_snmp(self):
        r = []
        # working but give vlan interface instead port name
        for v in self.snmp.get_tables(
            ["1.3.6.1.2.1.4.22.1.1", "1.3.6.1.2.1.4.22.1.2", "1.3.6.1.2.1.4.22.1.3"]
        ):
            iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[1], cached=True)  # IF-MIB
            mac = ":".join(["%02x" % ord(c) for c in v[2]])
            ip = ["%02x" % ord(c) for c in v[3]]
            ip = ".".join(str(int(c, 16)) for c in ip)
            r += [{"ip": ip, "mac": mac, "interface": iface}]
        return r

    def execute_cli(self):
        r = []
        for match in self.rx_line.finditer(self.cli("display arp", cached=True)):
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                continue
            iface = match.group("interface")
            iface = iface.replace("GE", "Gi ")
            iface = iface.replace("BAGG", "Po ")
            r += [{"ip": match.group("ip"), "mac": match.group("mac"), "interface": iface}]
        return r
