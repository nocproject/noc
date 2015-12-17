# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_capabilities"

    CHECK_SNMP_GET = {
        "BRAS | PPPoE": mib["CISCO-PPPOE-MIB::cPppoeSystemCurrSessions", 0],
        "BRAS | L2TP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 2],
        "BRAS | PPTP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 3]
    }

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp neighbors")
        return "% LLDP is not enabled" not in r

    @false_on_cli_error
    def has_cdp(self):
        """
        Check box has cdp enabled
        """
        r = self.cli("show cdp neighbors")
        return "% CDP is not enabled" not in r

    @false_on_cli_error
    def has_oam(self):
        """
        Check box has oam enabled
        """
        r = self.cli("show ethernet oam summary")
        return "% OAM is not enabled" not in r  # @todo:  not tested
