# ---------------------------------------------------------------------
# Eltex.MES.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.text import parse_table
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.MES.get_capabilities"

    rx_lldp_en = re.compile(r"LLDP state: Enabled?")
    rx_lacp_en = re.compile(r"\s+Partner[\S\s]+?\s+Oper Key:\s+1", re.MULTILINE)
    rx_gvrp_en = re.compile(r"GVRP Feature is currently Enabled on the device?")
    rx_stp_en = re.compile(r"Spanning tree enabled mode?")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled on Eltex
        """
        cmd = self.cli("show lldp configuration", ignore_errors=True)
        return self.rx_lldp_en.search(cmd) is not None

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled on Eltex
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpStatsRemTablesInserts", 0])
        if r:
            return True

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has lacp enabled on Eltex
        """
        cmd = self.cli("show lacp Port-Channel", ignore_errors=True)
        return self.rx_lacp_en.search(cmd) is not None

    @false_on_snmp_error
    def has_lacp_snmp(self):
        """
        Check box has lacp enabled on Eltex
        """
        for oid, value in self.snmp.getnext(mib["IEEE8023-LAG-MIB::dot3adAggPortPartnerOperKey"]):
            if value:
                return True
        return False

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled on Eltex
        """
        cmd = self.cli("show spanning-tree", ignore_errors=True)
        return self.rx_stp_en.search(cmd) is not None

    @false_on_snmp_error
    def has_stp_snmp(self):
        """
        Check box has stp enabled on Eltex
        """
        # RADLAN-BRIDGEMIBOBJECTS-MIB::rldot1dStpEnable
        r = self.snmp.get("1.3.6.1.4.1.89.57.2.3.0")
        return r == 1

    @false_on_cli_error
    def has_gvrp_cli(self):
        """
        Check box has gvrp enabled on Eltex
        """
        cmd = self.cli("show gvrp configuration", ignore_errors=True)
        return self.rx_gvrp_en.search(cmd) is not None
        # Get GVRP interfaces

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show version", cached=True)
        s = [e[0] for e in parse_table(r)]
        if not s:  # MES3324
            r = self.cli("show system", cached=True)
            if "Unit" not in r:  # MES3108F
                return []
            s = [e[0] for e in parse_table(r, footer=r"^Unit\s*(?:Main Power|Fans Status)")]
            while s[-1] == "":
                del s[-1]
        return s

    @false_on_snmp_error
    def has_stack_snmp(self):
        """
        Check stack members
        :return:
        """
        r = []
        mode = self.snmp.get(mib["RADLAN-STACK-MIB::rlStackUnitMode", 0])
        if mode == 1:
            return []
        for oid, stack_num in self.snmp.getnext(
            mib["RADLAN-STACK-MIB::rlStackActiveUnitIdAfterReset"]
        ):
            r += [str(stack_num)]
        return r

    @false_on_snmp_error
    def has_qos_interface_stats(self):
        # eltCountersQosStatisticsEnable
        # On config enabled by 'qos statistics interface'
        r = self.snmp.get("1.3.6.1.4.1.35265.1.23.1.8.1.1.2.1.0")
        if r == 1:
            # qos statistics interface
            return True

    def execute_platform_cli(self, caps):
        s = self.has_stack()
        if s:
            caps["Stack | Members"] = len(s) if len(s) >= 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
        s = self.has_qos_interface_stats()
        if s:
            caps["Metrics | QOS | Statistics"] = True

    def execute_platform_snmp(self, caps):
        s = self.has_stack_snmp()
        if s:
            caps["Stack | Members"] = len(s) if len(s) >= 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
        s = self.has_qos_interface_stats()
        if s:
            caps["Metrics | QOS | Statistics"] = True
