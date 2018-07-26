# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Alstec.MSPU.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []
    MAX_REPETITIONS = 40
    MAX_GETNEXT_RETIRES = 0

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    def get_iftable(self, oid):
        if "::" in oid:
            oid = mib[oid]
        for oid, v in self.snmp.getnext(oid,
                                        max_repetitions=self.get_max_repetitions(),
                                        max_retries=self.get_getnext_retires()):
            yield int(oid.rsplit(".", 1)[-1]), v

    def apply_table(self, r, mib, name, f=None):
        if not f:
            def f(x):
                return x
        for ifindex, v in self.get_iftable(mib):
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def get_data(self):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        unknown_interfaces = []
        for ifindex, name in self.get_iftable("IF-MIB::ifName"):
            try:
                v = self.profile.convert_interface_name(name)
            except InterfaceTypeError as e:
                self.logger.debug(
                    "Ignoring unknown interface %s: %s",
                    name, e
                )
                unknown_interfaces += [name]
                continue
            r[ifindex] = {
                "interface": v
            }
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply dot3StatsDuplexStatus
        self.apply_table(r, "EtherLike-MIB::dot3StatsDuplexStatus", "full_duplex", lambda x: x != 2)
        # Apply ifSpeed
        for ifindex, s in self.get_iftable("IF-MIB::ifSpeed"):
            ri = r.get(ifindex)
            if ri and "uplink" in ri["interface"]:
                s = int(s)
                ri["in_speed"] = s
                ri["out_speed"] = s
            elif ri and ri["interface"].startswith("h"):
                s = int(s)
                ri["in_speed"] = s // 1000
                ri["out_speed"] = s // 1000
            elif ri:
                s = int(s)
                ri["in_speed"] = s // 10
                ri["out_speed"] = s // 10

        return r.values()

    def execute_snmp(self):
        r = self.get_data()
        return r
