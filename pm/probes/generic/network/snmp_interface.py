## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP interface probes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.pm.probes.base import Probe, metric
from noc.lib.mib import mib


class SNMPInterfaceProbe(Probe):
    @metric(["Interface | Load | In", "Interface | Load | Out"],
            caps=["SNMP", "SNMP | IF-MIB"],
            convert=metric.COUNTER, scale=8,
            preference=metric.PREF_COMMON)
    def get_interface_load32(self, address, snmp__ro,
                           interface__ifindex, caps):
        return self.snmp_get(
            {
                "Interface | Load | In": mib["IF-MIB::ifInOctets", interface__ifindex],
                "Interface | Load | Out": mib["IF-MIB::ifOutOctets", interface__ifindex]
            },
            address=address, community=snmp__ro
        )

    @metric(["Interface | Errors | In", "Interface | Errors | Out"],
            caps=["SNMP", "SNMP | IF-MIB"],
            convert=metric.COUNTER,
            preference=metric.PREF_COMMON)
    def get_interface_errors(self, address, snmp__ro,
                             interface__ifindex, caps):
        return self.snmp_get(
            {
                "Interface | Errors | In": mib["IF-MIB::ifInErrors", interface__ifindex],
                "Interface | Errors | Out": mib["IF-MIB::ifOutErrors", interface__ifindex]
            },
            address=address, community=snmp__ro
        )

    @metric(["Interface | Discards | In", "Interface | Discards | Out"],
            caps=["SNMP", "SNMP | IF-MIB"],
            convert=metric.COUNTER,
            preference=metric.PREF_COMMON)
    def get_interface_discards(self, address, snmp__ro,
                               interface__ifindex, caps):
        return self.snmp_get(
            {
                "Interface | Discards | In": mib["IF-MIB::ifInDiscards", interface__ifindex],
                "Interface | Discards | Out": mib["IF-MIB::ifOutDiscards", interface__ifindex]
            },
            address=address, community=snmp__ro
        )

    @metric(["Interface | Load | In", "Interface | Load | Out"],
            caps=["SNMP", "SNMP | IF-MIB", "SNMP | IF-MIB | HC"],
            convert=metric.COUNTER, scale=8,
            preference=metric.PREF_COMMON + metric.PREF_BETTER
    )
    def get_interface_load64(self, address, snmp__ro,
                           interface__ifindex, caps):
        return self.snmp_get(
            {
                "Interface | Load | In": mib["IF-MIB::ifHCInOctets", interface__ifindex],
                "Interface | Load | Out": mib["IF-MIB::ifHCOutOctets", interface__ifindex]
            },
            address=address, community=snmp__ro
        )
