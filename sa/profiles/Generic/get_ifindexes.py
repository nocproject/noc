# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_ifindexes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes
from noc.lib.mib import mib


class Script(NOCScript):
    name = "Generic.get_ifindexes"
    implements = [IGetIfindexes]
    requires = []

    def execute(self):
        r = {}
        try:
            # 1.3.6.1.2.1.2.2.1.1 - IF-MIB::ifDescr
            for oid, v in self.snmp.getnext(mib["IF-MIB::ifDescr"]):
                v = self.profile.convert_interface_name(v)
                ifindex = int(oid.split(".")[-1])
                r[v] = ifindex
        except self.snmp.TimeOutError:
            pass
        return r
