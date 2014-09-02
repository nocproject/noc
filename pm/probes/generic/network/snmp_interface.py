# # -*- coding: utf-8 -*-
# #----------------------------------------------------------------------
# # SNMP interface probes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.pm.probes.base import Probe, metric


class SNMPInterfaceProbe(Probe):
    @metric(["Interface | Load | In", "Interface | Load | Out"],
            convert=metric.COUNTER, scale=8,
            preference=metric.PREF_COMMON)
    def get_interface_load(self, address, snmp__ro,
                           interface__ifindex):
        return self.snmp_get(
            {
                # IF-MIB::ifInOctets.{{interface__ifindex}}
                "Interface | Load | In": "1.3.6.1.2.1.2.2.1.10.%s" % interface__ifindex,
                # IF-MIB::ifOutOctets.{{interface__ifindex}}
                "Interface | Load | Out": "1.3.6.1.2.1.2.2.1.16.%s" % interface__ifindex
            },
            address=address, community=snmp__ro
        )

    @metric(["Interface | Errors | In", "Interface | Errors | Out"],
            convert=metric.COUNTER,
            preference=metric.PREF_COMMON)
    def get_interface_errors(self, address, snmp__ro,
                             interface__ifindex):
        return self.snmp_get(
            {
                # IF-MIB::ifInErrors.{{interface__ifindex}}
                "Interface | Errors | In": "1.3.6.1.2.1.2.2.1.14.%s" % interface__ifindex,
                # IF-MIB::ifOutErrors.{{interface__ifindex}}
                "Interface | Errors | Out": "1.3.6.1.2.1.2.2.1.20.%s" % interface__ifindex
            },
            address=address, community=snmp__ro
        )

    @metric(["Interface | Discards | In", "Interface | Discards | Out"],
            convert=metric.COUNTER,
            preference=metric.PREF_COMMON)
    def get_interface_discards(self, address, snmp__ro,
                               interface__ifindex):
        return self.snmp_get(
            {
                # IF-MIB::ifInDiscards.{{interface__ifindex}}
                "Interface | Discards | In": "1.3.6.1.2.1.2.2.1.13.%s" % interface__ifindex,
                # IF-MIB::ifOutDiscards.{{interface__ifindex}}
                "Interface | Discards | Out": "1.3.6.1.2.1.2.2.1.19.%s" % interface__ifindex
            },
            address=address, community=snmp__ro
        )
