# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_ifindex
##
## Generic SNMP-only version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetifindex import IGetIfIndex


class Script(BaseScript):
    name = "Generic.get_ifindex"
    interface = IGetIfIndex
    requires = []

    def execute(self, interface):
        try:
            # 1.3.6.1.2.1.2.2.1.1 - IF-MIB::ifDescr
            for oid, v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2"):
                v = self.profile.convert_interface_name(v)
                if v == interface:
                    return int(oid.split(".")[-1])
        except self.snmp.TimeOutError:
            return None
