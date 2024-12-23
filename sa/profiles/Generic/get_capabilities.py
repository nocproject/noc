# ---------------------------------------------------------------------
# Generic.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import functools
import itertools
from typing import List

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcapabilities import IGetCapabilities
from noc.core.mib import mib
from noc.core.snmp.version import SNMP_v1, SNMP_v2c, SNMP_v3
from noc.core.snmp.error import SNMPError
from noc.core.script.snmp.base import SNMP
from noc.core.text import filter_non_printable


def false_on_cli_error(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (BaseScript.CLIOperationError, BaseScript.CLISyntaxError):
            return False

    return wrapper


def false_on_snmp_error(f):
    @functools.wraps(f)
    def wrapper_snmp(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (SNMPError, SNMP.TimeOutError):
            return False

    return wrapper_snmp


class Script(BaseScript):
    name = "Generic.get_capabilities"
    interface = IGetCapabilities
    requires = []
    cache = True

    SNMP_GET_CHECK_OID = mib["SNMPv2-MIB::sysObjectID", 0]
    SNMP_BULK_CHECK_OID = mib["SNMPv2-MIB::sysDescr"]

    # Dict of capability -> oid to check against snmp GET
    CHECK_SNMP_GET = {}
    # Dict of capability -> oid to check against snmp GETNEXT
    CHECK_SNMP_GETNEXT = {}
    #
    CHECK_SNMP_GET_GENERIC = {
        "SNMP | MIB | HOST-RESOURCES-MIB": mib["HOST-RESOURCES-MIB::hrSystemDate", 0],
        "SNMP | MIB | NTPv4-MIB": mib["NTPv4-MIB::ntpEntStatusActiveRefSourceId", 0],
    }
    CHECK_SNMP_GETNEXT_GENERIC = {
        "SNMP | MIB | ADSL-MIB": mib["ADSL-LINE-MIB::adslLineCoding"],
    }
    #
    GET_SNMP_TABLE_IDX = {}
    #
    SNMP_CAPS = {SNMP_v1: "SNMP | v1", SNMP_v2c: "SNMP | v2c", SNMP_v3: "SNMP | v3"}
    # MIB Support

    def check_snmp_get(self, oid, version=None):
        """
        Check SNMP GET response to oid
        """
        try:
            r = self.snmp.get(oid, version=version)
            if r is not None and oid == mib["SNMPv2-MIB::sysObjectID", 0]:
                # For EnterpriseID Caps
                self._ent_id = r
            return r is not None
        except (self.snmp.TimeOutError, SNMPError):
            pass
        return False

    def check_snmp_getnext(self, oid, bulk=False, only_first=True, version=None):
        """
        Check SNMP response to GETNEXT/BULK
        """
        try:
            r = self.snmp.getnext(oid, bulk=bulk, only_first=only_first, version=version)
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

    def has_snmp_bulk(self):
        return self.check_snmp_getnext(self.SNMP_BULK_CHECK_OID, version=SNMP_v2c, bulk=True)

    def has_snmp_ifmib(self, version=None):
        """
        Check IF-MIB support
        """
        return self.check_snmp_getnext(mib["IF-MIB::ifIndex"], only_first=True, version=version)

    def has_snmp_ifmib_hc(self, version=None):
        """
        Check IF-MIB 64 bit counters
        """
        return self.check_snmp_getnext(
            mib["IF-MIB::ifHCInOctets"], only_first=True, version=version
        )

    def return_false(self, **kwargs):
        return False

    def has_lldp(self):
        """
        Returns True when LLDP is enabled
        """
        return self.call_method(
            cli_handler="has_lldp_cli",
            snmp_handler="has_lldp_snmp",
            fallback_handler=self.return_false,
        )

    def has_cdp(self):
        """
        Returns True when CDP is enabled
        """
        return self.call_method(
            cli_handler="has_cdp_cli",
            snmp_handler="has_cdp_snmp",
            fallback_handler=self.return_false,
        )

    def has_oam(self):
        """
        Returns True when OAM is enabled
        """
        return self.call_method(
            cli_handler="has_oam_cli",
            snmp_handler="has_oam_snmp",
            fallback_handler=self.return_false,
        )

    def has_stp(self):
        """
        Returns True when STP is enabled
        """
        return self.call_method(
            cli_handler="has_stp_cli",
            snmp_handler="has_stp_snmp",
            fallback_handler=self.return_false,
        )

    def has_udld(self):
        """
        Returns True when UDLD is enabled
        """
        return self.call_method(
            cli_handler="has_udld_cli",
            snmp_handler="has_udld_snmp",
            fallback_handler=self.return_false,
        )

    def has_ipv6(self):
        """
        Returns True when IPv6 ND is enabled
        """
        return self.call_method(
            cli_handler="has_ipv6_cli",
            snmp_handler="has_ipv6_snmp",
            fallback_handler=self.return_false,
        )

    def has_hsrp(self):
        """
        Returns True when HSRP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_hsrp_cli",
            snmp_handler="has_hsrp_snmp",
            fallback_handler=self.return_false,
        )

    def has_vrrp_v2(self):
        """
        Returns True when VRRP v2 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_vrrp_v2_cli",
            snmp_handler="has_vrrp_v2_snmp",
            fallback_handler=self.return_false,
        )

    def has_vrrp_v3(self):
        """
        Returns True when VRRP v3 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_vrrp_v3_cli",
            snmp_handler="has_vrrp_v3_snmp",
            fallback_handler=self.return_false,
        )

    def has_bgp(self):
        """
        Returns True when BGP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_bgp_cli",
            snmp_handler="has_bgp_snmp",
            fallback_handler=self.return_false,
        )

    def has_ospf_v2(self):
        """
        Returns True when OSPF v2 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_ospf_v2_cli",
            snmp_handler="has_ospf_v2_snmp",
            fallback_handler=self.return_false,
        )

    def has_ospf_v3(self):
        """
        Returns True when OSPF v3 is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_ospf_v3_cli",
            snmp_handler="has_ospf_v3_snmp",
            fallback_handler=self.return_false,
        )

    def has_isis(self):
        """
        Returns True when ISIS is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_isis_cli",
            snmp_handler="has_isis_snmp",
            fallback_handler=self.return_false,
        )

    def has_ldp(self):
        """
        Returns True when LDP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_ldp_cli",
            snmp_handler="has_ldp_snmp",
            fallback_handler=self.return_false,
        )

    def has_rsvp(self):
        """
        Returns True when RSVP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_rsvp_cli",
            snmp_handler="has_rsvp_snmp",
            fallback_handler=self.return_false,
        )

    def has_lacp(self):
        """
        Returns True when LACP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_lacp_cli",
            snmp_handler="has_lacp_snmp",
            fallback_handler=self.return_false,
        )

    def has_bfd(self):
        """
        Returns True when BFD is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_bfd_cli",
            snmp_handler="has_bfd_snmp",
            fallback_handler=self.return_false,
        )

    def has_rep(self):
        """
        Returns True when REP is enabled
        :return:
        """
        return self.call_method(
            cli_handler="has_rep_cli",
            snmp_handler="has_rep_snmp",
            fallback_handler=self.return_false,
        )

    def get_enterprise_id(self, version=None):
        """
        Returns EnterpriseID number from sysObjectID
        :param version:
        :return:
        """
        if self.has_snmp():
            try:
                r = getattr(self, "_ent_id", None)
                if r is None:
                    r = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0], version=version)
                elif len(r.split(".")) < 6:
                    # Bad values
                    r = self.snmp.getnext(
                        "1.3.6.1.4.1", bulk=False, version=version, only_first=True
                    )
                    if r:
                        r = r[0][0]
                return r
            except (self.snmp.TimeOutError, SNMPError):
                pass

    @false_on_snmp_error
    def get_sysdescr(self, version=None):
        """
        Returns data from sysDescr
        :param version
        :return:
        """
        if self.has_snmp():
            r = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], version=version)
            if not r:
                return None
            return filter_non_printable(r)

    @false_on_snmp_error
    def get_engine_id(self):
        """
        Return SNMPv3 EngineId
        """
        try:
            engine_id = self.snmp.get_engine_id()
        except NotImplementedError:
            return None
        self.logger.debug("EngineID: %s", engine_id)
        if engine_id:
            return engine_id.hex()
        return None

    def get_snmp_table_idx(self, oid) -> List[int]:
        r = []
        for oid, value in self.snmp.getnext(mib["HOST-RESOURCES-MIB::hrProcessorFrwID"]):
            _, idx = oid.rsplit(".", 1)
            r.append(str(idx))
        return r

    def execute_platform_cli(self, caps):
        """
        Method to be overriden in subclasses. Execute if C preffered
        :param caps: Dict of capabilities, can be modified
        """

    def execute_platform_snmp(self, caps):
        """
        Method to be overriden in subclasses. Execute if S prefferd
        :param caps: Dict of capabilities, can be modified
        """

    def execute_platform(self, caps):
        """
        Method to be overriden in subclasses.
        :param caps: Dict of capabilities, can be modified
        """

    def is_requested(self, section):
        """
        Check if section is requested
        :param section:
        :return:
        """
        if self.requested:
            return section in self.requested
        return True

    def execute(self, only=None):
        # Requested capabilities
        if only:
            self.requested = set(only)
        else:
            self.requested = None
        #
        caps = {}
        if self.is_requested("snmp"):
            snmp_version = None
            if self.is_requested("snmp_v1"):
                if self.check_snmp_get(self.SNMP_GET_CHECK_OID, version=SNMP_v1):
                    caps["SNMP | v1"] = True
                    snmp_version = SNMP_v1
                else:
                    caps["SNMP | v1"] = False
                self.snmp.close()
            if self.is_requested("snmp_v2c"):
                self.snmp.close()
                if self.check_snmp_get(self.SNMP_GET_CHECK_OID, version=SNMP_v2c):
                    caps["SNMP | v2c"] = True
                    snmp_version = SNMP_v2c
                    if self.has_snmp_bulk():
                        caps["SNMP | Bulk"] = True
                else:
                    caps["SNMP | v2c"] = False
                self.snmp.close()
            if self.is_requested("snmp_v2c"):
                if self.check_snmp_get(self.SNMP_GET_CHECK_OID, version=SNMP_v3):
                    caps["SNMP | v3"] = True
                    snmp_version = SNMP_v3
                    engine_id = self.get_engine_id()
                    if engine_id:
                        caps["SNMP | EngineID"] = engine_id
                    if self.has_snmp_bulk():
                        caps["SNMP | Bulk"] = True
                else:
                    caps["SNMP | v3"] = False
                self.snmp.close()
            if snmp_version is not None:
                # SNMP is enabled
                caps["SNMP"] = True
                # Update script's capabilities
                # for valid following snmp.get
                self.capabilities.update(caps)
                # Check mibs
                if self.has_snmp_ifmib(version=snmp_version):
                    caps["SNMP | IF-MIB"] = True
                    if self.has_snmp_ifmib_hc(version=snmp_version):
                        caps["SNMP | IF-MIB | HC"] = True
                for cap, oid in itertools.chain(
                    self.CHECK_SNMP_GET.items(), self.CHECK_SNMP_GET_GENERIC.items()
                ):
                    if self.check_snmp_get(oid, version=snmp_version):
                        caps[cap] = True
                for cap, oid in itertools.chain(
                    self.CHECK_SNMP_GETNEXT.items(),
                    self.CHECK_SNMP_GETNEXT_GENERIC.items(),
                ):
                    if self.check_snmp_getnext(oid, version=snmp_version):
                        caps[cap] = True
                for cap, oid in self.GET_SNMP_TABLE_IDX.items():
                    idx = self.get_snmp_table_idx(oid)
                    if idx:
                        caps[cap] = " | ".join(str(x) for x in idx)
                x = self.get_enterprise_id(version=snmp_version)
                if x:
                    caps["SNMP | OID | sysObjectID"] = x
                    if len(x.split(".")) > 6:
                        caps["SNMP | OID | EnterpriseID"] = int(x.split(".")[6])
                sysdescr = self.get_sysdescr(version=snmp_version)
                if sysdescr:
                    caps["SNMP | OID | sysDescr"] = sysdescr
            else:
                caps["SNMP"] = False
        else:
            caps["SNMP"] = False
            for v in self.SNMP_CAPS:
                caps[v] = False
        if self.is_requested("stp") and self.has_stp():
            caps["Network | STP"] = True
        if self.is_requested("lldp") and self.has_lldp():
            caps["Network | LLDP"] = True
        if self.is_requested("cdp") and self.has_cdp():
            caps["Network | CDP"] = True
        if self.is_requested("oam") and self.has_oam():
            caps["Network | OAM"] = True
        if self.is_requested("udld") and self.has_udld():
            caps["Network | UDLD"] = True
        if self.has_ipv6():
            caps["Network | IPv6"] = True
        if self.is_requested("hsrp") and self.has_hsrp():
            caps["Network | HSRP"] = True
        if self.is_requested("vrrp") and self.has_vrrp_v2():
            caps["Network | VRRP | v2"] = True
        if self.is_requested("vrrpv3") and self.has_vrrp_v3():
            caps["Network | VRRP | v3"] = True
        if self.is_requested("bgp") and self.has_bgp():
            caps["Network | BGP"] = True
        if self.is_requested("ospf") and self.has_ospf_v2():
            caps["Network | OSPF | v2"] = True
        if self.is_requested("ospfv3") and self.has_ospf_v3():
            caps["Network | OSPF | v3"] = True
        if self.is_requested("isis") and self.has_isis():
            caps["Network | ISIS"] = True
        if self.is_requested("ldp") and self.has_ldp():
            caps["Network | LDP"] = True
        if self.is_requested("rsvp") and self.has_rsvp():
            caps["Network | RSVP"] = True
        if self.is_requested("lacp") and self.has_lacp():
            caps["Network | LACP"] = True
        if self.is_requested("bfd") and self.has_bfd():
            caps["Network | BFD"] = True
        if self.is_requested("rep") and self.has_rep():
            caps["Network | REP"] = True
        self.call_method(
            cli_handler="execute_platform_cli",
            snmp_handler="execute_platform_snmp",
            fallback_handler="execute_platform",
            **{"caps": caps},
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
