# ---------------------------------------------------------------------
# Nateks.NetXpert.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mac import MAC
from noc.core.mib import mib
from noc.core.ip import IPv4
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Nateks.NetXpert.get_interfaces"
    cache = True
    interface = IGetInterfaces

    MAX_REPETITIONS = 20

    MAX_GETNEXT_RETIRES = 0

    INTERFACE_TYPES = {
        1: "other",
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
        117: "physical",  # gigabitEthernet
        135: "SVI",  # l2vlan
        161: "aggregated",  # ieee8023adLag
        53: "SVI",  # propVirtual
    }

    INTERFACE_NAMES = set()

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def collect_ifnames(self):
        return self.INTERFACE_NAMES

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    def get_ifindexes(self):
        r = {}
        unknown_interfaces = []
        if self.has_snmp():
            try:
                for oid, name in self.snmp.getnext(
                    mib["IF-MIB::ifDescr"],
                    max_repetitions=self.get_max_repetitions(),
                    max_retries=self.get_getnext_retires(),
                ):
                    try:
                        v = self.profile.convert_interface_name(name)
                    except InterfaceTypeError as why:
                        self.logger.debug("Ignoring unknown interface %s: %s", name, why)
                        unknown_interfaces += [name]
                        continue
                    ifindex = int(oid.split(".")[-1])
                    r[v] = ifindex
                if unknown_interfaces:
                    self.logger.info(
                        "%d unknown interfaces has been ignored", len(unknown_interfaces)
                    )
            except self.snmp.TimeOutError:
                pass
        return r

    def get_iftable(self, oid, transform=True):
        if "::" in oid:
            oid = mib[oid]
        for oid, v in self.snmp.getnext(
            oid, max_repetitions=self.get_max_repetitions(), max_retries=self.get_getnext_retires()
        ):
            yield int(oid.rsplit(".", 1)[-1]) if transform else oid, v

    def apply_table(self, r, mib, name, f=None):
        if not f:

            def f(x):
                return x

        for ifindex, v in self.get_iftable(mib):
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def get_ip_ifaces(self):
        ip_iface = {
            l: ".".join(o.rsplit(".")[-4:])
            for o, l in self.get_iftable("1.3.6.1.2.1.4.20.1.2", False)
        }
        ip_mask = {
            ".".join(o.rsplit(".")[-4:]): l
            for o, l in self.get_iftable("1.3.6.1.2.1.4.20.1.3", False)
        }
        r = {}
        for ip in ip_iface:
            r[ip] = (ip_iface[ip], ip_mask[ip_iface[ip]])
        return r

    def execute_snmp(self, interface=None, last_ifname=None):
        last_ifname = self.collect_ifnames()
        # v = self.scripts.get_interface_status_ex()
        index = self.scripts.get_ifindexes()
        # index = self.get_ifindexes()
        ifaces = {index[i]: {"interface": i} for i in index}
        # Apply ifAdminStatus
        self.apply_table(ifaces, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(ifaces, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply PhysAddress
        self.apply_table(ifaces, "IF-MIB::ifPhysAddress", "mac_address")
        self.apply_table(ifaces, "IF-MIB::ifType", "type")
        self.apply_table(ifaces, "IF-MIB::ifSpeed", "speed")
        self.apply_table(ifaces, "IF-MIB::ifMtu", "mtu")
        self.apply_table(ifaces, "IF-MIB::ifAlias", "description")
        ip_ifaces = self.get_ip_ifaces()
        r = []
        subs = defaultdict(list)
        """
        IF-MIB::ifPhysAddress.1 = STRING:
        IF-MIB::ifPhysAddress.2 = STRING: 0:21:5e:40:c2:50
        IF-MIB::ifPhysAddress.3 = STRING: 0:21:5e:40:c2:52
        """
        for l in ifaces:
            iface = ifaces[l]
            # If the bug in the firmware and the number of interfaces in cli is
            # different from the number of interfaces given through snmp,
            # we pass the list of interfaces for reconciliation.
            # def execute_snmp(self, interface=None, last_ifname= None):
            #     IFNAME = set(["Gi 1/0/1", "Gi 1/0/2", "Gi 1/0/3", "Gi 1/0/4", "Gi 1/0/5", "Gi 1/0/6", "Gi 1/0/7",
            #                   "Gi 1/0/8", "Gi 1/0/9", "Gi 1/0/10", "Gi 1/0/11", "Gi 1/0/12", "Po 1", "Po 2", "Po 3",
            #                   "Po 4", "Po 5", "Po 6","Po 7", "Po 8", "Po 9", "Po 10", "Po 11", "Po 12", "Po 13",
            #                   "Po 14", "Po 15", "Po 16"])
            #     if self.match_version(version__regex="4\.0\.8\.1$") and self.match_version(platform__regex="MES-2308P"):
            #         return super().execute_snmp(last_ifname=IFNAME)
            if last_ifname and iface["interface"] not in last_ifname:
                continue
            i_type = self.INTERFACE_TYPES.get(iface["type"], "other")
            if "." in iface["interface"]:
                s = {
                    "name": iface["interface"],
                    "description": iface.get("description", ""),
                    "type": i_type,
                    "enabled_afi": ["BRIDGE"],
                    "admin_status": iface["admin_status"],
                    "oper_status": iface["oper_status"],
                    "snmp_ifindex": l,
                }
                iface_name, num = iface["interface"].rsplit(".", 1)
                if num.isdigit():
                    vlan_ids = int(iface["interface"].rsplit(".", 1)[-1])
                    if vlan_ids < 4000:
                        s["vlan_ids"] = vlan_ids
                if l in ip_ifaces:
                    s["ipv4_addresses"] = [IPv4(*ip_ifaces[l])]
                    s["enabled_afi"] = ["IPv4"]
                if iface["mac_address"]:
                    s["mac"] = MAC(iface["mac_address"])
                subs[iface_name] += [s.copy()]
                # r[-1]["subinterfaces"] += [s]
                continue
            i = {
                "name": iface["interface"],
                "description": iface.get("description", ""),
                "type": i_type,
                "admin_status": iface["admin_status"],
                "oper_status": iface["oper_status"],
                "snmp_ifindex": l,
            }
            if iface["mac_address"]:
                i["mac"] = MAC(iface["mac_address"])
            # sub = {"subinterfaces": [i.copy()]}
            r += [i]
        for l in r:
            if l["name"] in subs:
                l["subinterfaces"] = subs[l["name"]]
            else:
                l["subinterfaces"] = [
                    {
                        "name": l["name"],
                        "description": l.get("description", ""),
                        "type": "SVI",
                        "enabled_afi": (
                            ["BRIDGE"] if l["type"] in ["physical", "aggregated"] else []
                        ),
                        "admin_status": l["admin_status"],
                        "oper_status": l["oper_status"],
                        "snmp_ifindex": l["snmp_ifindex"],
                    }
                ]
        return [{"interfaces": r}]
