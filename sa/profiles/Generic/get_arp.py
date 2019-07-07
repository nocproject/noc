# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Generic.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.mib import mib
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Generic.get_arp"
    cache = True
    interface = IGetARP

    def execute_snmp(self, vrf=None, **kwargs):
        r = []
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        for oid, mac in self.snmp.getnext(mib["RFC1213-MIB::ipNetToMediaPhysAddress"]):
            ifindex, ip = oid[21:].split(".", 1)
            ifname = names.get(int(ifindex))
            if ifname:
                r += [{"ip": ip, "mac": MAC(mac), "interface": ifname}]
        return r
