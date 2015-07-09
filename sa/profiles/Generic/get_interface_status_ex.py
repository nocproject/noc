# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_interface_status_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.lib.mib import mib


class Script(NOCScript):
    name = "Generic.get_interface_status_ex"
    implements = [IGetInterfaceStatusEx]
    requires = []

    def get_iftable(self, oid):
        if "::" in oid:
            oid = mib[oid]
        r = {}
        for oid, v in self.snmp.getnext(oid):
            ifindex = int(oid.split(".")[-1])
            r[ifindex] = v
        return r

    def apply_table(self, r, mib, name, f=None):
        if not f:
            f = lambda x: x
        d = self.get_iftable(mib)
        for ifindex in d:
            if ifindex in r:
                r[ifindex][name] = f(d[ifindex])

    def get_data(self):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        for ifindex, name in self.get_iftable("IF-MIB::ifDescr").iteritems():
            try:
                v = self.profile.convert_interface_name(name)
            except InterfaceTypeError, why:
                self.logger.info(
                    "Ignoring unknown interface %s: %s",
                    v, why
                )
                continue
            r[ifindex] = {
                "interface": v
            }
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: str(x) == "1")
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: str(x) == "1")
        # Apply ifSpeed
        s_table = self.get_iftable("IF-MIB::ifSpeed")
        hs_table = self.get_iftable("IF-MIB::ifHighSpeed")
        for ifindex in r:
            hs = hs_table.get(ifindex)
            if hs is not None:
                hs = int(hs)
                if hs:
                    r[ifindex]["in_speed"] = hs * 1000
                    r[ifindex]["out_speed"] = hs * 1000
                    continue
            s = s_table.get(ifindex)
            if s is not None:
                s = int(s)
                if s:
                    r[ifindex]["in_speed"] = s // 1000
                    r[ifindex]["out_speed"] = s // 1000
                    continue                    
        return r.values()

    def execute(self):
        r = {}
        try:
            return self.get_data()
        except self.snmp.TimeOutError:
            return []
