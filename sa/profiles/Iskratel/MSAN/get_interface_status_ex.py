# ---------------------------------------------------------------------
# Iskratel.MSAN.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Iskratel.MSAN.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def get_iftable(self, oid):
        if "::" in oid:
            oid = mib[oid]
        r = {}
        for oid, v in self.snmp.getnext(oid, max_repetitions=40):
            ifindex = int(oid.split(".")[-1])
            r[ifindex] = v
        return r

    def apply_table(self, r, mib, name, f=None):
        f = f or (lambda x: x)
        d = self.get_iftable(mib)
        for ifindex in d:
            if ifindex in r:
                r[ifindex][name] = f(d[ifindex])

    def get_teplate_bw(self, templates):
        # Template xdsl2ChConfProfMaxDataRateUs
        base_oid_in = "1.3.6.1.2.1.10.251.1.5.2.1.1.7."
        # Template xdsl2ChConfProfMaxDataRateDs
        base_oid_out = "1.3.6.1.2.1.10.251.1.5.2.1.1.6."
        oids = {}
        for templ_name in templates:
            index = str(len(templ_name)) + "." + ".".join([str(ord(s)) for s in templ_name])
            oids[templ_name + "UP"] = base_oid_in + index
            oids[templ_name + "DOWN"] = base_oid_out + index
        if not oids:
            return {}
        return self.snmp.get(oids)

    def get_data(self, interfaces=None):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        unknown_interfaces = []
        if interfaces:
            for i in interfaces:
                r[i["ifindex"]] = {"interface": i["interface"]}
        else:
            for ifindex, name in self.get_iftable("IF-MIB::ifName").items():
                try:
                    v = self.profile.convert_interface_name(name)
                except InterfaceTypeError as why:
                    self.logger.debug("Ignoring unknown interface %s: %s", name, why)
                    unknown_interfaces += [name]
                    continue
                r[ifindex] = {"interface": v}
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply ifSpeed
        s_table = self.get_iftable("IF-MIB::ifSpeed")
        # Get xdsl2LineStatusActTemplate
        s_templ_table = self.get_iftable("1.3.6.1.2.1.10.251.1.1.1.1.12")
        highspeed = set()
        s_templ = {}
        if s_templ_table:
            s_templ = self.get_teplate_bw(set(s_templ_table.values()))
        for ifindex in r:
            s = s_table.get(ifindex)
            if s is not None:
                s = int(s)
                if s == 4294967295:
                    highspeed.add(ifindex)
                elif s:
                    r[ifindex]["in_speed"] = s // 1000
                    r[ifindex]["out_speed"] = s // 1000
            else:
                s = s_templ_table.get(ifindex)
                if s is not None:
                    r[ifindex]["in_speed"] = int(s_templ.get(s + "DOWN", 0)) // 1000
                    r[ifindex]["out_speed"] = int(s_templ.get(s + "UP", 0)) // 1000
        # Refer to ifHighSpeed if necessary
        if highspeed:
            hs_table = self.get_iftable("IF-MIB::ifHighSpeed")
            for ifindex in highspeed:
                s = hs_table.get(ifindex)
                if s is not None:
                    s = int(s)
                    if s:
                        r[ifindex]["in_speed"] = s * 1000
                        r[ifindex]["out_speed"] = s * 1000
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored", len(unknown_interfaces))
        return list(r.values())

    def execute_snmp(self, interfaces=None, **kwargs):
        return self.get_data(interfaces=interfaces)
