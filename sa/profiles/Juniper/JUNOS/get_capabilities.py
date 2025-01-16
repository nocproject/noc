# ---------------------------------------------------------------------
# Juniper.JUNOS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib
from noc.core.validators import is_int
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Juniper.JUNOS.get_capabilities"

    CHECK_SNMP_GETNEXT = {
        "Juniper | OID | jnxCosIfqStatsTable": mib["JUNIPER-COS-MIB::jnxCosIfqQedPkts"],
    }
    CHECK_SNMP_GET = {
        "Metrics | Subscribers": "1.3.6.1.4.1.2636.3.64.1.1.1.2.0",
    }

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        r = self.cli("show spanning-tree bridge | match Enabled")
        if "?STP" in r or "MSTP" in r:
            return True
        return False

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp | match Enabled")
        return "Enabled" in r

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        for v, r in self.snmp.getnext(mib["LLDP-MIB::lldpPortConfigTLVsTxEnable"], bulk=False):
            if r != smart_text("\x00"):
                return True
        return False

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has oam enabled
        """
        r = self.scripts.get_oam_status()
        return bool(r)

    # def has_oam_snmp(self):
    #    # on qfx3500 14.1X53-D46.7 return nothing
    #
    #    """
    #    Check box has oam enabled
    #    """
    #    # dot3OamAdminState
    #    for v, r in self.snmp.getnext("1.3.6.1.2.1.158.1.1.1.1", bulk=False):
    #        if is_int(r) and int(r) == 1:  # enabled(1)
    #            return True
    #    return False

    @false_on_cli_error
    def has_bfd_cli(self):
        """
        Check box has bfd enabled
        """
        r = self.cli("show bfd session")
        return "0 sessions, 0 clients" not in r

    @false_on_snmp_error
    def has_bfd_snmp(self):
        """
        Check box has bfd enabled
        """
        # bfdAdminStatus
        bfd = self.snmp.get("1.3.6.1.4.1.2636.5.3.1.1.1.1.0")
        if is_int(bfd) and int(bfd) == 1:  # enabled(1)
            return True
        return False

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has lacp enabled
        """
        r = self.cli("show lacp interfaces")
        return "lacp subsystem not running" not in r

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
    def get_rpm_probes(self):
        v = self.scripts.get_sla_probes()
        return len(v)

    @false_on_cli_error
    def has_cli_help(self):
        """
        Check device CLI help.. command supported
        :return:
        """
        self.cli("help")
        return True

    @false_on_snmp_error
    def has_ppoe_snmp(self):
        # jnxPPPoEMajorInterfaceCount
        pppoe = self.snmp.get("1.3.6.1.4.1.2636.3.67.1.1.3.1.0")
        return is_int(pppoe) and int(pppoe) > 0

    @false_on_snmp_error
    def has_l2tp_snmp(self):
        # jnxL2tpStatsTotalTunnels
        l2tp = self.snmp.get("1.3.6.1.4.1.2636.3.49.1.1.1.1.1.0")
        return is_int(l2tp) and int(l2tp) > 0

    @false_on_snmp_error
    def has_dhcp_snmp(self):
        #  jnxTotalAuthenticationResponses
        dhcp = self.snmp.get("1.3.6.1.4.1.2636.3.51.1.1.1.2.0")
        return is_int(dhcp) and int(dhcp) > 0

    def execute_platform_cli(self, caps):
        np = self.get_rpm_probes()
        if np > 0:
            caps["Juniper | RPM | Probes"] = np
        if self.has_cli_help():
            caps["Juniper | CLI | Help"] = True

    def execute_platform_snmp(self, caps):
        np = 0
        # jnxRpmResSumSent
        for v, r in self.snmp.getnext("1.3.6.1.4.1.2636.3.50.1.2.1.2", bulk=False):
            tests = v.split(".")
            if tests[-1] == "1":  # currentTest(1)
                np += 1
        if np > 0:
            caps["Juniper | RPM | Probes"] = np
        if self.has_ppoe_snmp():
            caps["BRAS | PPPoE"] = True
        if self.has_l2tp_snmp():
            caps["BRAS | L2TP"] = True
        if self.has_dhcp_snmp():
            caps["Network | DHCP"] = True
        # jnxVirtualChassisMemberRole
        role = {1: "master", 2: "backup", 3: "linecard"}
        vs = {}
        for v, r in self.snmp.getnext("1.3.6.1.4.1.2636.3.40.1.4.1.1.1.3", bulk=False):
            oid = v.split(".")[-1]
            vs[oid] = role[r]
        if vs and len(vs) > 1:
            caps["Stack | Members"] = len(vs)
            caps["Stack | Member Ids"] = " | ".join([str(v) for v in vs])
