# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_ifindexes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes
from noc.sa.interfaces.base import InterfaceTypeError
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Generic.get_ifindexes"
    interface = IGetIfindexes
    requires = []

    def execute(self):
        r = {}
        unknown_interfaces = []
        if self.has_snmp():
            try:
                for oid, name in self.snmp.getnext(mib["IF-MIB::ifDescr"]):
                    try:
                        v = self.profile.convert_interface_name(name)
                    except InterfaceTypeError, why:
                        self.logger.debug(
                            "Ignoring unknown interface %s: %s",
                            name, why
                        )
                        unknown_interfaces += [name]
                        continue
                    ifindex = int(oid.split(".")[-1])
                    r[v] = ifindex
                if unknown_interfaces:
                    self.logger.info("%d unknown interfaces has been ignored",
                                     len(unknown_interfaces))
            except self.snmp.TimeOutError:
                pass
        return r
