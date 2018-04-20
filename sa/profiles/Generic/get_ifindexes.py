# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Generic.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_ifindexes"
    interface = IGetIfindexes
    requires = []

    def execute_snmp(self):
        r = {}
        unknown_interfaces = []
        for oid, name in self.snmp.getnext(mib["IF-MIB::ifDescr"]):
            try:
                v = self.profile.convert_interface_name(name)
            except InterfaceTypeError as e:
                self.logger.debug(
                    "Ignoring unknown interface %s: %s",
                    name, e
                )
                unknown_interfaces += [name]
                continue
            ifindex = int(oid.split(".")[-1])
            r[v] = ifindex
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored",
                             len(unknown_interfaces))
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
