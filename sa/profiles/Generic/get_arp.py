# ----------------------------------------------------------------------
# Generic.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.mib import mib
from noc.core.mac import MAC
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Generic.get_arp"
    cache = True
    interface = IGetARP

    def execute_snmp(self, vrf=None, **kwargs):
        r = []
        names = {x: y for y, x in self.scripts.get_ifindexes().items()}
        for oid, mac in self.snmp.getnext(
            mib["RFC1213-MIB::ipNetToMediaPhysAddress"],
            display_hints={mib["RFC1213-MIB::ipNetToMediaPhysAddress"]: render_mac},
        ):
            ifindex, ip = oid[21:].split(".", 1)
            ifname = names.get(int(ifindex))
            if ifname and mac:
                r += [{"ip": ip, "mac": MAC(mac), "interface": ifname}]
            elif ifname:
                r += [{"ip": ip, "interface": ifname}]
        return r
