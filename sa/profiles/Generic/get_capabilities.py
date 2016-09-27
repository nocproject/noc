# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import functools
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcapabilities import IGetCapabilities
from noc.lib.mib import mib
from noc.core.snmp.consts import SNMP_v1, SNMP_v2c, SNMP_v3


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
        SNMP_v2c: "SNMP | v2",
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
            except self.snmp.TimeOutError:
                pass
        return False

    def check_snmp_getnext(self, oid, bulk=False, only_first=True):
        """
        Check SNMP response to GETNEXT/BULK
        """
        try:
            for k, v in self.snmp.getnext(oid, bulk=bulk,
                                          only_first=only_first):
                return True
        except self.snmp.TimeOutError:
            pass
        return False

    def has_snmp(self):
        """
        Check basic SNMP support
        """
        return self.check_snmp_get(self.SNMP_GET_CHECK_OID)

    def get_snmp_version(self):
        """
        Get SNMP version
        :return: Working SNMP version or None
        """
        for v in self.SNMP_VERSIONS:
            if self.check_snmp_get(self.SNMP_GET_CHECK_OID, version=v):
                return v
        return None

    def has_snmp_bulk(self):
        return self.check_snmp_getnext(self.SNMP_BULK_CHECK_OID,
                                       bulk=True)

    def has_snmp_ifmib(self):
        """
        Check IF-MIB support
        """
        return self.check_snmp_getnext(mib["IF-MIB::ifIndex"],
                                       only_first=True)

    def has_snmp_ifmib_hc(self):
        """
        Check IF-MIB 64 bit counters
        """
        return self.check_snmp_getnext(mib["IF-MIB::ifHCInOctets"],
                                       only_first=True)

    def has_lldp(self):
        """
        Returns True when LLDP is enabled
        """
        return False

    def has_cdp(self):
        """
        Returns True when CDP is enabled
        """
        return False

    def has_oam(self):
        """
        Returns True when OAM is enabled
        """
        return False

    def has_stp(self):
        """
        Returns True when STP is enabled
        """
        return False

    def has_udld(self):
        """
        Returns True when UDLD is enabled
        """
        return False

    def execute_platform(self, caps):
        """
        Method to be overriden in subclasses.
        :param caps: Dict of capabilities, can be modified
        """
        pass

    def execute(self):
        caps = {}
        sv = self.get_snmp_version()
        if sv is not None:
            # SNMP is enabled
            caps["SNMP"] = True
            for v in self.SNMP_CAPS:
                caps[self.SNMP_CAPS[v]] = v == sv
            if sv != SNMP_v1 and self.has_snmp_bulk():
                caps["SNMP | Bulk"] = True
            if self.has_snmp_ifmib():
                caps["SNMP | IF-MIB"] = True
                if self.has_snmp_ifmib_hc():
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
        self.execute_platform(caps)
        return caps


def false_on_cli_error(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (BaseScript.CLIOperationError, BaseScript.CLISyntaxError):
            return False
    return wrapper
