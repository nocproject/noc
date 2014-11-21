## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic SNMP ARP Probes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.pm.probes.base import Probe, metric
from noc.lib.mib import mib


class CiscoIOSBRAS(Probe):
    @metric("BRAS | PPPoE | Sessions",
            profile="Cisco.IOS",
            caps=["SNMP", "BRAS | PPPoE"],
            preference=metric.PREF_VENDOR)
    def get_snmp_pppoe_sessions(self, address, snmp__ro, *args, **kwargs):
        return self.snmp_get(
            mib["CISCO-PPPOE-MIB::cPppoeSystemCurrSessions", 0],
            address, community=snmp__ro
        )

    @metric("BRAS | L2TP | Sessions",
            profile="Cisco.IOS",
            caps=["SNMP", "BRAS | L2TP"],
            preference=metric.PREF_VENDOR)
    def get_snmp_pptp_sessions(self, address, snmp__ro, *args, **kwargs):
        return self.snmp_get(
            mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 2],
            address, community=snmp__ro
        )

    @metric("BRAS | PPTP | Sessions",
            profile="Cisco.IOS",
            caps=["SNMP", "BRAS | PPTP"],
            preference=metric.PREF_VENDOR)
    def get_snmp_pptp_sessions(self, address, snmp__ro, *args, **kwargs):
        return self.snmp_get(
            mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 3],
            address, community=snmp__ro
        )
