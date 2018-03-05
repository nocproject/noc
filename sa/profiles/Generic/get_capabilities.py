# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import functools
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcapabilities import IGetCapabilities
from noc.core.mib import mib
from noc.core.snmp.version import SNMP_v1, SNMP_v2c, SNMP_v3
from noc.core.snmp.error import SNMPError


class Script(BaseScript):
    name = "Generic.get_capabilities"
    interface = IGetCapabilities
    requires = []
    cache = True

    SNMP_GET_CHECK_OID = mib["SNMPv2-MIB::sysObjectID", 0]
    SNMP_BULK_CHECK_OID = mib["SNMPv2-MIB::sysDescr"]

    # Dict of capability -> oid to check against snmp GET
    CHECK_SNMP_GET = {}
    #
    SNMP_VERSIONS = (SNMP_v2c, SNMP_v1)
    #
    SNMP_CAPS = {
        SNMP_v1: "SNMP | v1",
        SNMP_v2c: "SNMP | v2c",
        SNMP_v3: "SNMP | v3"
    }

    def check_snmp_get(self, oid, version=None):
        """
        Check SNMP GET response to oid
        """
        if self.credentials.get("snmp_ro"):
            try:
                r = self.snmp.get(oid, version=version)
                return r is not None
            except (self.snmp.TimeOutError, SNMPError):
                pass
        return False

    def check_snmp_getnext(self, oid, bulk=False, only_first=True, version=None):
        """
        Check SNMP response to GETNEXT/BULK
        """
        try:
            r = self.snmp.getnext(oid, bulk=bulk,
                                  only_first=only_first,
                                  version=version)
            return r and any(r)
        except (self.snmp.TimeOutError, SNMPError):
            return False

    def has_snmp(self):
        """
        Check basic SNMP support
        """
        r = getattr(self, "_has_snmp", None)
        if r is None:
            r = self.check_snmp_get(self.SNMP_GET_CHECK_OID)
            self._has_snmp = r
        return r

    def get_snmp_versions(self):
        """
        Get SNMP version
        :return: Working SNMP versions set or empty set
        """
        sv = set()
        for v in self.SNMP_VERSIONS:
            if self.check_snmp_get(self.SNMP_GET_CHECK_OID, version=v):
                sv.add(v)
        return sv

    def has_snmp_bulk(self):
        return self.check_snmp_getnext(self.SNMP_BULK_CHECK_OID,
                                       bulk=True)

    def has_snmp_ifmib(self, version=None):
        """
        Check IF-MIB support
        """
        return self.check_snmp_getnext(mib["IF-MIB::ifIndex"],
                                       only_first=True,
                                       version=version)

    def has_snmp_ifmib_hc(self, version=None):
        """
        Check IF-MIB 64 bit counters
        """
        return self.check_snmp_getnext(mib["IF-MIB::ifHCInOctets"],
                                       only_first=True,
                                       version=version)

    def return_false(self, **kwargs):
        return False

    def has_lldp(self):
        """
        Returns True when LLDP is enabled
        """
        return self.call_method(
            cli_handler="has_lldp_cli",
            snmp_handler="has_lldp_snmp",
            fallback_handler=self.return_false
        )

    def has_cdp(self):
        """
        Returns True when CDP is enabled
        """
        return self.call_method(
            cli_handler="has_cdp_cli",
            snmp_handler="has_cdp_snmp",
            fallback_handler=self.return_false
        )

    def has_oam(self):
        """
        Returns True when OAM is enabled
        """
        return self.call_method(
            cli_handler="has_oam_cli",
            snmp_handler="has_oam_snmp",
            fallback_handler=self.return_false
        )

    def has_stp(self):
        """
        Returns True when STP is enabled
        """
        return self.call_method(
            cli_handler="has_stp_cli",
            snmp_handler="has_stp_snmp",
            fallback_handler=self.return_false
        )

    def has_udld(self):
        """
        Returns True when UDLD is enabled
        """
        return self.call_method(
            cli_handler="has_udld_cli",
            snmp_handler="has_udld_snmp",
            fallback_handler=self.return_false
        )

    def has_ipv6(self):
        """
        Returns True when IPv6 ND is enabled
        """
        return self.call_method(
            cli_handler="has_ipv6_cli",
            snmp_handler="has_ipv6_snmp",
            fallback_handler=self.return_false
        )

    def has_hsrp(self):
        """
        Returns True when HSRP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_hsrp_cli",
            snmp_handler="has_hsrp_snmp",
            fallback_handler=self.return_false
        )

    def has_vrrp_v2(self):
        """
        Returns True when VRRP v2 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_vrrp_v2_cli",
            snmp_handler="has_vrrp_v2_snmp",
            fallback_handler=self.return_false
        )

    def has_vrrp_v3(self):
        """
        Returns True when VRRP v3 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_vrrp_v3_cli",
            snmp_handler="has_vrrp_v3_snmp",
            fallback_handler=self.return_false
        )

    def has_bgp(self):
        """
        Returns True when BGP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_bgp_cli",
            snmp_handler="has_bgp_snmp",
            fallback_handler=self.return_false
        )

    def has_ospf_v2(self):
        """
        Returns True when OSPF v2 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_ospf_v2_cli",
            snmp_handler="has_ospf_v2_snmp",
            fallback_handler=self.return_false
        )

    def has_ospf_v3(self):
        """
        Returns True when OSPF v3 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_ospf_v3_cli",
            snmp_handler="has_ospf_v3_snmp",
            fallback_handler=self.return_false
        )

    def has_isis(self):
        """
        Returns True when ISIS is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_isis_cli",
            snmp_handler="has_isis_snmp",
            fallback_handler=self.return_false
        )

    def has_ldp(self):
        """
        Returns True when LDP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_ldp_cli",
            snmp_handler="has_ldp_snmp",
            fallback_handler=self.return_false
        )

    def has_rsvp(self):
        """
        Returns True when RSVP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_rsvp_cli",
            snmp_handler="has_rsvp_snmp",
            fallback_handler=self.return_false
        )

    def has_lacp(self):
        """
        Returns True when LACP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_lacp_cli",
            snmp_handler="has_lacp_snmp",
            fallback_handler=self.return_false
        )

    def has_bfd(self):
        """
        Returns True when BFD is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_bfd_cli",
            snmp_handler="has_bfd_snmp",
            fallback_handler=self.return_false
        )

    def has_rep(self):
        """
        Returns True when REP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_rep_cli",
            snmp_handler="has_rep_snmp",
            fallback_handler=self.return_false
        )

    def execute_platform_cli(self, caps):
        """
        Method to be overriden in subclasses. Execute if C preffered
        :param caps: Dict of capabilities, can be modified
        """
        pass

    def execute_platform_snmp(self, caps):
        """
        Method to be overriden in subclasses. Execute if S prefferd
        :param caps: Dict of capabilities, can be modified
        """
        pass

    def execute_platform(self, caps):
        """
        Method to be overriden in subclasses.
        :param caps: Dict of capabilities, can be modified
        """
        pass

    def execute(self):
        caps = {}
        svs = self.get_snmp_versions()
        if svs:
            # SNMP is enabled
            caps["SNMP"] = True
            self.capabilities["SNMP"] = True
            for v in self.SNMP_CAPS:
                caps[self.SNMP_CAPS[v]] = v in svs
                self.capabilities[self.SNMP_CAPS[v]] = v in svs
            if svs & set([SNMP_v2c, SNMP_v3]) and self.has_snmp_bulk():
                caps["SNMP | Bulk"] = True
            if self.has_snmp_ifmib(version=list(svs)[-1]):
                caps["SNMP | IF-MIB"] = True
                if self.has_snmp_ifmib_hc(list(svs)[-1]):
                    caps["SNMP | IF-MIB | HC"] = True
            for cap, oid in self.CHECK_SNMP_GET.iteritems():
                if self.check_snmp_get(oid):
                    caps[cap] = True
        else:
            caps["SNMP"] = False
            for v in self.SNMP_CAPS:
                caps[v] = False
        if self.has_stp():
            caps["Network | STP"] = True
        if self.has_lldp():
            caps["Network | LLDP"] = True
        if self.has_cdp():
            caps["Network | CDP"] = True
        if self.has_oam():
            caps["Network | OAM"] = True
        if self.has_udld():
            caps["Network | UDLD"] = True
        if self.has_ipv6():
            caps["Network | IPv6"] = True
        if self.has_hsrp():
            caps["Network | HSRP"] = True
        if self.has_vrrp_v2():
            caps["Network | VRRP | v2"] = True
        if self.has_vrrp_v3():
            caps["Network | VRRP | v3"] = True
        if self.has_bgp():
            caps["Network | BGP"] = True
        if self.has_ospf_v2():
            caps["Network | OSPF | v2"] = True
        if self.has_ospf_v3():
            caps["Network | OSPF | v3"] = True
        if self.has_isis():
            caps["Network | ISIS"] = True
        if self.has_ldp():
            caps["Network | LDP"] = True
        if self.has_rsvp():
            caps["Network | RSVP"] = True
        if self.has_lacp():
            caps["Network | LACP"] = True
        if self.has_bfd():
            caps["Network | BFD"] = True
        if self.has_rep():
            caps["Network | REP"] = True
        self.call_method(
            cli_handler="execute_platform_cli",
            snmp_handler="execute_platform_snmp",
            fallback_handler="execute_platform",
            **{"caps": caps}
        )
        return caps

    def get_syntax_variant(self, commands):
        """
        Executes commands until correct syntax found
        :param commands: list of commands
        :return: Index of first working command or None, if none working
        """
        for i, cmd in enumerate(commands):
            try:
                self.cli(cmd)
                return i
            except (BaseScript.CLIOperationError, BaseScript.CLISyntaxError):
                pass
        return None

    def apply_capability(self, name, value):
        """
        Apply capability to capabilities immediately
        :param name:
        :param value:
        :return:
        """
        self.capabilities[name] = value


def false_on_cli_error(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (BaseScript.CLIOperationError, BaseScript.CLISyntaxError):
            return False
    return wrapper
