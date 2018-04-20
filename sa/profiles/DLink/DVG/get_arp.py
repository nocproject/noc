# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## DLink.DVG.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetARP


class Script(noc.sa.script.Script):
    name = "DLink.DVG.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True

    def execute(self):
        r = []
<<<<<<< HEAD
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
=======
        # BUG http://bt.nocproject.org/browse/NOC-36
        # Only one way: SNMP.
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for ip, mac, i in self.snmp.join_tables("1.3.6.1.2.1.4.22.1.3",
                                                        "1.3.6.1.2.1.4.22.1.2",
                                                        "1.3.6.1.2.1.4.22.1.1",
                                                        bulk=True,
                                                        cached=True):  # IP-MIB
                    r += [{"ip": ip, "mac": mac, "interface": self.snmp.get(
                        "1.3.6.1.2.1.2.2.1.2" + '.' + i, cached=True)}]  # IF-MIB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
