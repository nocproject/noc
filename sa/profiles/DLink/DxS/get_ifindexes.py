# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_ifindexes
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
    name = "DLink.DxS.get_ifindexes"
    interface = IGetIfindexes
    cache = True

    def execute_snmp(self):
        r = {}
        ifnames = {}
        old_dlink = False
        unknown_interfaces = []
        for oid, name in self.snmp.getnext(mib["IF-MIB::ifName"], cached=True):
            ifindex = int(oid.split(".")[-1])
            if ifindex == 1 and name.startswith("Slot0/"):
                old_dlink = True
            if old_dlink:
                v = self.profile.convert_interface_name(name)
                r[v] = ifindex
            if ifindex < 5121:
                continue
            ifnames[ifindex] = name
        if old_dlink:
            return r
        for oid, name in self.snmp.getnext(mib["IF-MIB::ifDescr"], cached=True):
            ifindex = int(oid.split(".")[-1])
            if ifindex < 1024:  # physical interfaces
                try:
                    v = self.profile.convert_interface_name(name)
                except InterfaceTypeError as why:
                    self.logger.debug(
                        "Ignoring unknown interface %s: %s", name, why
                    )
                    unknown_interfaces += [name]
                    continue
                r[v] = ifindex
            elif ifindex >= 1024 and ifindex < 5121:  # 802.1q vlans
                continue
            elif ifindex >= 5121:  # L3 interfaces
                v = ifnames[ifindex]
                r[v] = ifindex
        if unknown_interfaces:
            self.logger.info(
                "%d unknown interfaces has been ignored",
                len(unknown_interfaces)
            )
        return r
