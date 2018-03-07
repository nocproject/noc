# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Generic.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.mib import mib
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Generic.get_arp"
    cache = True
    interface = IGetARP
    MAX_REPETITIONS = 40

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def execute_snmp(self, **kwargs):
        r = []
        ifindexes = self.scripts.get_ifindexes(max_rep=self.get_max_repetitions())
        ifmap = dict((ifindex, ifindexes[ifindex]) for ifindex in ifindexes)
        for oid, mac in self.snmp.getnext(mib["RFC1213-MIB::ipNetToMediaPhysAddress"], max_repetitions=self.get_max_repetitions()):
            ifindex, ip = oid[21:].split(".", 1)
            ifname = ifmap.get(int(ifindex))
            if ifname:
                r += [{
                    "ip": ip,
                    "mac": MAC(mac),
                    "interface": ifname
                }]
        return r
