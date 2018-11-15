# -*- coding: utf-8 -*-
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
    name = "Eltex.MES.get_ifindexes"
    interface = IGetIfindexes
    cache = True
    requires = []

    MAX_GETNEXT_RETIRES = 0
    INTERFACE_NAME_OID = "IF-MIB::ifDescr"

    def get_interface_name_oid(self):
        return self.INTERFACE_NAME_OID

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    def execute_snmp(self, name_oid=None):
        if not name_oid:
            name_oid = self.get_interface_name_oid()
        r = {}
        unknown_interfaces = []
        for oid, name in self.snmp.getnext(mib[name_oid], max_retries=self.get_getnext_retires()):
            ifindex = int(oid.split(".")[-1])
            try:
                v = self.profile.convert_interface_name(name)
            except InterfaceTypeError as e:
                self.logger.debug("Ignoring unknown interface %s: %s", name, e)
                unknown_interfaces += [name]
                continue
            r[v] = ifindex
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored", len(unknown_interfaces))
        return r
