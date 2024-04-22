# ---------------------------------------------------------------------
# Cisco.IOS.get_capabilities_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib
from noc.core.validators import is_int


class Script(BaseScript):
    name = "Cisco.IOS.get_capabilities"

    CHECK_SNMP_GET = {
        "BRAS | PPPoE": mib["CISCO-PPPOE-MIB::cPppoeSystemCurrSessions", 0],
        "BRAS | L2TP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 2],
        "BRAS | PPTP": mib["CISCO-VPDN-MGMT-MIB::cvpdnSystemTunnelTotal", 3],
    }

    CHECK_SNMP_GETNEXT = {
        "Cisco | MIB | CISCO-CLASS-BASED-QOS-MIB": mib[
            "CISCO-CLASS-BASED-QOS-MIB::cbQosIFPolicyIndex", 0
        ]
    }

    CAP_SLA_SYNTAX = "Cisco | IOS | Syntax | IP SLA"

    SYNTAX_IP_SLA_APPLICATION = ["show ip sla application", "show ip sla monitor application"]

    SYNTAX_IP_SLA_RESPONDER = ["show ip sla responder", "show ip sla monitor responder"]

    SYNTAX_IP_SLA_CONFIGURATION = ["show ip sla configuration", "show ip sla monitor configuration"]

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpLocChassisIdSubtype", 0])
        return is_int(r) and r >= 1

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp neighbors")
        return "% LLDP is not enabled" not in r

    @false_on_snmp_error
    def has_cdp_snmp(self):
        """
        Check box has cdp enabled
        """
        r = self.snmp.get(mib["CISCO-CDP-MIB::cdpGlobalRun", 0])
        return r == 1

    @false_on_cli_error
    def has_cdp_cli(self):
        """
        Check box has cdp enabled
        """
        r = self.cli("show cdp neighbors")
        return "% CDP is not enabled" not in r

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has oam enabled
        """
        r = self.cli("show ethernet oam summary")
        return "% OAM is not enabled" not in r  # @todo:  not tested

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show spanning-tree")
        if "No spanning tree instance exists" in r or "No spanning tree instances exist" in r:
            return False
        return True

    @false_on_cli_error
    def has_udld_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show udld  neighbors")
        if len(r.splitlines()) > 2:
            return True
        return False

    @false_on_cli_error
    def has_bfd_cli(self):
        """
        Check box has bfd enabled
        """
        r = self.cli("show bfd summary")
        if not r:
            return False
        return True

    @false_on_cli_error
    def has_ipv6_cli(self):
        """
        Check box has IPv6 ND enabled
        """
        self.cli("show ipv6 neighbors")
        return True

    rx_ip_sla_responder = re.compile(
        r"IP SLA Monitor Responder is:\s*(?P<state>\S+)", re.MULTILINE | re.IGNORECASE
    )

    @false_on_cli_error
    def has_ip_sla_responder_cli(self):
        r = self.cli(self.SYNTAX_IP_SLA_RESPONDER[self.capabilities[self.CAP_SLA_SYNTAX]])
        match = self.rx_ip_sla_responder.search(r)
        if match:
            return "enabled" in match.group("state").lower()
        else:
            return False

    @false_on_snmp_error
    def has_ip_sla_responder_snmp(self):
        r = self.snmp.get(mib["CISCO-RTTMON-MIB::rttMonApplResponder", 0])
        return r != 2

    rx_ip_sla_probe_entry = re.compile(r"Entry Number: \d+", re.IGNORECASE | re.MULTILINE)

    @false_on_cli_error
    def get_ip_sla_probes_cli(self):
        r = self.cli(self.SYNTAX_IP_SLA_CONFIGURATION[self.capabilities[self.CAP_SLA_SYNTAX]])
        return sum(1 for _ in self.rx_ip_sla_probe_entry.finditer(r))

    @false_on_snmp_error
    def get_ip_sla_probes_snmp(self):
        r = self.snmp.count(mib["CISCO-RTTMON-MIB::rttMonCtrlAdminStatus"])
        return r

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check LACP Status
        :return:
        """
        r = self.cli("show lacp counters")
        return r

    @false_on_cli_error
    def has_rep_cli(self):
        """
        Check REP status
        :return:
        """
        r = self.cli("show rep topology")
        return bool(r)

    @false_on_cli_error
    def has_ldp_cli(self):
        """
        Check box has LDP enabled
        """
        self.cli("show mpls ldp parameters")
        return True

    @false_on_cli_error
    def has_hsrp_cli(self):
        """
        Check box has HSRP enabled
        """
        v = self.cli("show standby").strip()
        return bool(v)

    @false_on_cli_error
    def has_vrrp_v2_cli(self):
        """
        Check box has VRRPv2 enabled
        """
        v = self.cli("show vrrp brief", cached=True).splitlines()
        return True if len(v) > 1 else False

    @false_on_cli_error
    def has_vrrp_v3_cli(self):
        """
        Check box has VRRPv3 enabled
        """
        v = self.cli("show vrrp detail")
        return bool(v)

    @false_on_snmp_error
    def has_ip_sla_probes(self):
        return self.snmp.get(mib["CISCO-RTTMON-MIB::rttMonApplProbeCapacity", 0])

    def execute_platform_cli(self, caps):
        # Check IP SLA status
        sla_v = self.get_syntax_variant(self.SYNTAX_IP_SLA_APPLICATION)
        if sla_v is not None:
            # Set syntax
            self.apply_capability(self.CAP_SLA_SYNTAX, sla_v)
            caps[self.CAP_SLA_SYNTAX] = sla_v
            # IP SLA responder
            if self.has_ip_sla_responder_cli():
                caps["Cisco | IP | SLA | Responder"] = True
            # IP SLA Probes
            np = self.get_ip_sla_probes_cli()
            if np:
                caps["Cisco | IP | SLA | Probes"] = np

    def execute_platform_snmp(self, caps):
        sla_v = self.has_ip_sla_probes()
        if sla_v:
            # IP SLA responder
            if self.has_ip_sla_responder_snmp():
                caps["Cisco | IP | SLA | Responder"] = True
            # IP SLA Probes
            np = self.get_ip_sla_probes_snmp()
            if np:
                caps["Cisco | IP | SLA | Probes"] = np
