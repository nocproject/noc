# # -*- coding: utf-8 -*-
# #----------------------------------------------------------------------
## Generic SNMP ARP Probes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.pm.probes.base import Probe, metric
from noc.lib.mib import mib


class SNMPARPProbe(Probe):
    @metric("IP | ARP | Count",
            caps=["SNMP"],
            preference=metric.PREF_COMMON)
    def get_object_arp_rfc1213(self, address, snmp__ro, caps):
        return self.snmp_count(
            mib["RFC1213-MIB::ipNetToMediaPhysAddress"],
            address, community=snmp__ro,
            bulk=caps.get("SNMP | Bulk", False)
        )

    @metric("IP | ARP | Count",
            caps=["SNMP"],
            preference=metric.PREF_COMMON + metric.PREF_BETTER)
    def get_interface_arp_rfc1213(self, address, snmp__ro,
                                  interface__ifindex, caps):
        filter = lambda oid, value: int(oid.split(".")[-5]) == interface__ifindex
        return self.snmp_count(
            mib["RFC1213-MIB::ipNetToMediaPhysAddress"],
            address, community=snmp__ro, filter=filter,
            bulk=caps.get("SNMP | Bulk", False)
        )
