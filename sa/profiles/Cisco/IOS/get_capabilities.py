# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_capabilities"

    CHECK_SNMP_GET = {
        "BRAS | PPPoE": mib["CISCO-PPPOE-MIB::cPppoeSystemCurrSessions", 0],
        "BRAS | L2TP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 2],
        "BRAS | PPTP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 3]
    }

    CAP_SLA_SYNTAX = "Cisco | IOS | Syntax | IP SLA"

    SYNTAX_IP_SLA_APPLICATION = [
        "show ip sla application",
        "show ip sla monitor application"
    ]

    SYNTAX_IP_SLA_RESPONDER = [
        "show ip sla responder",
        "show ip sla monitor responder"
    ]

    SYNTAX_IP_SLA_CONFIGURATION = [
        "show ip sla configuration",
        "show ip sla monitor configuration"
    ]

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

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show spanning-tree")
        if ("No spanning tree instance exists" in r
            or "No spanning tree instances exist" in r):
            return False
        return True

    @false_on_cli_error
    def has_ipv6(self):
        """
        Check box has IPv6 ND enabled
        """
        self.cli("show ipv6 neighbors")
        return True

    rx_ip_sla_responder = re.compile(
        r"IP SLA Monitor Responder is:\s*(?P<state>\S+)",
        re.MULTILINE | re.IGNORECASE
    )

    @false_on_cli_error
    def has_ip_sla_responder(self):
        r = self.cli(
            self.SYNTAX_IP_SLA_RESPONDER[self.capabilities[self.CAP_SLA_SYNTAX]]
        )
        match = self.rx_ip_sla_responder.search(r)
        if match:
            return "enabled" in match.group("state").lower()
        else:
            return False

    rx_ip_sla_probe_entry = re.compile("Entry Number: \d+",
                                       re.IGNORECASE | re.MULTILINE)

    @false_on_cli_error
    def get_ip_sla_probes(self):
        r = self.cli(
            self.SYNTAX_IP_SLA_CONFIGURATION[self.capabilities[self.CAP_SLA_SYNTAX]]
        )
        return sum(1 for _ in self.rx_ip_sla_probe_entry.finditer(r))

    @false_on_cli_error
    def has_lacp(self):
        """
        Check LACP Status
        :return:
        """
        r = self.cli("show lacp counters")
        return r

    def execute_platform(self, caps):
        # Check IP SLA status
        sla_v = self.get_syntax_variant(self.SYNTAX_IP_SLA_APPLICATION)
        if sla_v is not None:
            # Set syntax
            self.apply_capability(self.CAP_SLA_SYNTAX, sla_v)
            caps[self.CAP_SLA_SYNTAX] = sla_v
            # IP SLA responder
            if self.has_ip_sla_responder():
                caps["Cisco | IP | SLA | Responder"] = True
            # IP SLA Probes
            np = self.get_ip_sla_probes()
            if np:
                caps["Cisco | IP | SLA | Probes"] = np
            if self.has_lacp():
                caps["Network | LACP"] = True
