# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.mib import mib
from noc.core.mac import MAC


class Script(BaseScript):
    name = "DLink.DVG.get_arp"
    interface = IGetARP
    cache = True

    def execute(self):
        r = []
        if self.has_snmp():
            try:
                ifindexes = self.scripts.get_ifindexes()
                ifmap = dict((ifindexes[ifindex], ifindex) for ifindex in ifindexes)
                for oid, mac in self.snmp.getnext(mib["RFC1213-MIB::ipNetToMediaPhysAddress"]):
                    ifindex, ip = oid[21:].split(".", 1)
                    ifname = ifmap.get(int(ifindex))
                    if ifname:
                        r += [{
                            "ip": ip,
                            "mac": MAC(mac),
                            "interface": ifname
                        }]
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
