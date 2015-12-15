# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcapabilities import IGetCapabilities
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Generic.get_capabilities"
    interface = IGetCapabilities
    requires = []
    cache = True

    # Dict of capability -> oid to check against snmp GET
    CHECK_SNMP_GET = {}

    def check_snmp_get(self, oid):
        """
        Check SNMP GET response to oid
        """
        if self.credentials.get("snmp_ro"):
            try:
                self.snmp.get(oid)
                return True
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
        return self.check_snmp_get(mib["SNMPv2-MIB::sysObjectID", 0])

    def has_snmp_bulk(self):
        return self.check_snmp_getnext(mib["SNMPv2-MIB::sysDescr"],
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

    def execute_platform(self, caps):
        """
        Method to be overriden in subclasses.
        :param caps: Dict of capabilities, can be modified
        """
        pass

    def execute(self):
        caps = {}
        if self.has_snmp():
            caps["SNMP"] = True
            if self.has_snmp_bulk():
                caps["SNMP | Bulk"] = True
            if self.has_snmp_ifmib():
                caps["SNMP | IF-MIB"] = True
                if self.has_snmp_ifmib_hc():
                    caps["SNMP | IF-MIB | HC"] = True
            for cap, oid in self.CHECK_SNMP_GET.itervalues():
                if self.check_snmp_get(oid):
                    caps[cap] = True
        if self.has_lldp():
            caps["Network | LLDP"] = True
        if self.has_cdp():
            caps["Network | CDP"] = True
        if self.has_oam():
            caps["Network | OAM"] = True
        return caps
