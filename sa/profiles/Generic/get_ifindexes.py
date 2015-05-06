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
from noc.sa.interfaces.base import InterfaceTypeError
from noc.lib.mib import mib


class Script(NOCScript):
    name = "Generic.get_ifindexes"
    implements = [IGetIfindexes]
    requires = []

    def execute(self):
        r = {}
        try:
            for oid, v in self.snmp.getnext(mib["IF-MIB::ifDescr"]):
                try:
                    v = self.profile.convert_interface_name(v)
                except InterfaceTypeError, why:
                    self.logger.info(
                        "Ignoring unknown interface %s: %s",
                        v, why
                    )
                    continue
                ifindex = int(oid.split(".")[-1])
                r[v] = ifindex
        except self.snmp.TimeOutError:
            pass
        return r
