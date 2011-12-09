# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Nortel.BayStack425.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "Nortel.BayStack425.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_dynamic = re.compile(r"^(?P<mac1>\S+)\s+Port:\s+(?P<port1>\d+)\s*"
                            r"((?P<mac2>\S+)\s+Port:\s+(?P<port2>\d+))*")
    rx_static = re.compile(r"^(?P<port>\d+)\s+(?P<mac>\S+)")
    rx_pvids = re.compile(r"^(?P<port>\S+)\s+(?P<vid>\d+)\s+")

    def execute(self, interface=None, vlan=None, mac=None):
        # Read PVID table
        cmd = "show vlan interface vids"
        v = self.cli(cmd)
        pvids = {}
        for l in v.split("\n"):
            match = self.rx_pvids.match(l)
            if match:
                pvids[match.group("port")] = match.group("vid")
        r = []
        # Read dynamic MACs
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += " address %s" % mac
        elif interface is not None:
            cmd += " port %s" % interface
        v = self.cli(cmd)
        for l in v.split("\n"):
            match = self.rx_dynamic.match(l.strip())
            if match:
                skip1 = skip2 = 0
                if vlan is not None:
                    skip1 = skip2 = 1
                    if int(pvids.get(match.group("port1"))) == int(vlan):
                        skip1 = 0
                    if match.group("port2"):
                        if int(pvids.get(match.group("port2"))) == int(vlan):
                            skip2 = 0

                if not skip1:
                    r += [{
                        "vlan_id": pvids.get(match.group("port1")),
                        "mac": match.group("mac1").replace("-", ":"),
                        "interfaces": [match.group("port1")],
                        "type": "D"
                    }]

                if not skip2 and match.group("mac2"):
                    r += [{
                        "vlan_id": pvids.get(match.group("port2")),
                        "mac": match.group("mac2").replace("-", ":"),
                        "interfaces": [match.group("port2")],
                        "type": "D"
                    }]
        # Read static MACs
        cmd = "show mac-security mac-address-table"
        v = self.cli(cmd)
        for l in v.split("\n"):
            match = self.rx_static.match(l.strip())
            if match:
                skip = 0
                if (mac is not None and
                    match.group("mac").replace("-", ":") != mac):
                    skip = 1
                if interface is not None and match.group("port") != interface:
                    skip = 1
                if (vlan is not None and
                   int(pvids.get(match.group("port"))) != int(vlan)):
                    skip = 1
                if not skip:
                    r += [{
                        "vlan_id": pvids.get(match.group("port")),
                        "mac": match.group("mac").replace("-", ":"),
                        "interfaces": [match.group("port")],
                        "type": "S"
                    }]
        return r
