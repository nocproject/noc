# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcapabilitiesex import IGetCapabilitiesEx
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_capabilities_ex"
    cache = True
    interface = IGetCapabilitiesEx

    CAPS_OIDS = {
        "BRAS | PPPoE": mib["CISCO-PPPOE-MIB::cPppoeSystemCurrSessions", 0],
        "BRAS | L2TP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 2],
        "BRAS | PPTP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 3]
    }

    def execute(self, caps={}):
        if caps.get("SNMP"):
            for c, oid in self.CAPS_OIDS.iteritems():
                if self.has_oid(oid):
                    caps[c] = True
        return caps
