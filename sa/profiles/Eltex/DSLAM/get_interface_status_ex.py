# ---------------------------------------------------------------------
# Eltex.DSLAM.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.DSLAM.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def get_iftable(self, oid):
        if "::" in oid:
            oid = mib[oid]
        r = {}
        for oid, v in self.snmp.getnext(oid, max_repetitions=8):
            if oid.endswith(".0"):
                ifindex = int(oid.split(".")[-2])
            else:
                ifindex = int(oid.split(".")[-1])
            r[ifindex] = v
        return r

    def apply_table(self, r, oid, name, f=None):
        if not f:

            def f(x):
                return x

        for ifindex, v in self.get_iftable(oid).items():
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def get_data(self):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        for ifindex, name in self.get_iftable("IF-MIB::ifName").items():
            if " " in name:
                name = name.split()[2]
            if name.startswith("p"):
                name = "s%s" % name
            r[ifindex] = {"interface": name}
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply dot3StatsDuplexStatus
        self.apply_table(r, "EtherLike-MIB::dot3StatsDuplexStatus", "full_duplex", lambda x: x != 2)
        # Apply ifSpeed
        for ifindex, s in self.get_iftable("IF-MIB::ifSpeed").items():
            ri = r.get(ifindex)
            if ri:
                s = int(s)
                ri["in_speed"] = s // 1000
                ri["out_speed"] = s // 1000

        return list(r.values())

    def get_data_sw(self, o):
        # ifIndex -> ifName mapping
        sw_oid = "%s.15.2.1.2" % o
        r = {}  # ifindex -> data
        for ifindex, name in self.get_iftable(sw_oid).items():
            if " " in name:
                name = name.split()[2]
            if name.startswith("p"):
                name = "s%s" % name
            r[ifindex] = {"interface": name}
        # Apply ifAdminStatus
        self.apply_table(r, "%s.15.2.1.3" % o, "admin_status", lambda x: x == "UP" or "1")
        # Apply ifOperStatus
        self.apply_table(r, "%s.15.2.1.3" % o, "oper_status", lambda x: x == "UP" or "1")
        # Apply ifSpeed
        for ifindex, s in self.get_iftable("%s.15.2.1.4" % o).items():
            ri = r.get(ifindex)
            if isinstance(s, int):
                s = s
            elif " " in str(s):
                s = s.split()[0]
            else:
                s = 0
            if ri:
                s = int(s)
                ri["in_speed"] = s * 1000
                ri["out_speed"] = s * 1000
        return list(r.values())

    def get_data_adsl(self, o):
        # ifIndex -> ifName mapping
        if self.is_platform_MXA32 or self.is_platform_MXA64:
            s_oid = "%s.10.2.1.5" % o
        else:
            s_oid = "%s.10.2.1.7" % o
        adsl_oid = "%s.10.2.1.2" % o
        r = {}  # ifindex -> data
        for ifindex, name in self.get_iftable(adsl_oid).items():
            r[ifindex] = {"interface": name}

        # Apply ifAdminStatus
        self.apply_table(r, "%s.10.2.1.3" % o, "admin_status", lambda x: x in ("up", 1))
        # Apply ifOperStatus
        self.apply_table(r, "%s.10.2.1.3" % o, "oper_status", lambda x: x in ("up", 1))
        # Apply ifSpeed
        for ifindex, s in self.get_iftable(s_oid).items():
            ri = r.get(ifindex)
            if ri:
                s = int(s)
                ri["in_speed"] = s
                ri["out_speed"] = s
        return list(r.values())

    def execute_snmp(self, interfaces=None):
        if self.is_platform_MXA24:
            o = "1.3.6.1.4.1.34300.1.6"
        elif self.is_platform_MXA32:
            o = "1.3.6.1.4.1.35265.1.28"
        else:
            o = "1.3.6.1.4.1.35265.1.33"
        if self.is_platform_MXA24:
            r = self.get_data_sw(o)
        else:
            r = self.get_data()
        r += self.get_data_adsl(o)
        return r
