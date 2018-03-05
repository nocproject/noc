# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DVG.get_ifindexes"
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
        return r
