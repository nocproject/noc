# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetcapabilities import IGetCapabilities
from noc.lib.mib import mib


class Script(NOCScript):
    name = "Generic.get_capabilities"
    implements = [IGetCapabilities]
    requires = []

    def check_ifmib_hc(self, caps):
        """
        Check IF-MIB 64 bit counters
        """
        try:
            for k, v in self.snmp.getnext(mib["IF-MIB::ifHCInOctets"], only_first=True):
                caps["SNMP | IF-MIB | HC"] = True
                return
        except self.snmp.TimeOutError:
            return

    def check_ifmib(self, caps):
        """
        Check IF-MIB support
        """
        try:
            for k, v in self.snmp.getnext(mib["IF-MIB::ifIndex"], only_first=True):
                caps["SNMP | IF-MIB"] = True
                self.check_ifmib_hc(caps)
                return
        except self.snmp.TimeOutError:
            return

    def check_snmp(self, caps):
        """
        Check basic SNMP support
        """
        if not self.snmp and self.access_profile.snmp_ro:
            return
        try:
            self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0])
        except self.snmp.TimeOutError:
            return
        caps["SNMP"] = True
        self.check_ifmib(caps)

    def execute(self):
        caps = {}
        self.check_snmp(caps)
        if self.scripts.has_script("get_capabilities_ex"):
            caps = self.scripts.get_capabilities_ex(caps=caps)
        return caps
