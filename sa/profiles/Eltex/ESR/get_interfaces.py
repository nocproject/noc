# ---------------------------------------------------------------------
# Eltex.ESR.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table
from noc.core.mib import mib
from noc.core.validators import is_ipv4, is_ipv6


class Script(BaseScript):
    name = "Eltex.ESR.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(r"Interface:?\s+(?P<iface>\S+)")

    types = {"gi": "physical", "te": "physical", "po": "aggregated", "br": "SVI"}

    def execute_cli(self, interface=None):
        stp = []
        c = self.cli("show spanning-tree active", cached=True)
        for ifname, state, prio, cost, status, role, portfast, ptype in parse_table(
            c, allow_wrap=True
        ):
            stp += [ifname]
        vrrp = []
        c = self.cli("show vrrp", cached=True)
        for router, v_ip, pri, pre, state in parse_table(c, allow_wrap=True):
            v = self.cli("show vrrp %s" % router)
            match = self.rx_iface.search(v)
            vrrp += [match.group("iface")]
        descriptions = {}
        c = self.cli("show interfaces description", cached=True)
        for ifname, astate, lstate, descr in parse_table(c):
            if descr != "--":
                descriptions[ifname] = descr
        ip_addresses = {}
        c = self.cli("show ip interfaces", cached=True)
        for line in parse_table(c):
            # When type is DHCP, IP address may be '--'
            if is_ipv4(line[0]):
                ip_addresses[line[1]] = line[0]
        ipv6_addresses = {}
        c = self.cli("show ipv6 interfaces", cached=True)
        for line in parse_table(c):
            if is_ipv6(line[0]):
                ipv6_addresses[line[1]] = line[0]
        interfaces = []
        c = self.cli("show interfaces status", cached=True)
        # ESR-12V ver.1.0.9 produce random empty lines
        c = "\n".join([s for s in c.split("\n") if s])
        for line in parse_table(c, allow_wrap=True):
            # In some cases may be over 5 columns
            ifname = line[0]
            astate = line[1]
            lstate = line[2]
            mtu = line[3]
            mac = line[4]
            description = descriptions.get(ifname)
            sub = {
                "name": ifname,
                "admin_status": astate == "Up",
                "oper_status": lstate == "Up",
                "mtu": mtu,
                "mac": mac,
                "enabled_afi": [],
                "enabled_protocols": [],
            }
            if ip_addresses.get(ifname):
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [ip_addresses.get(ifname)]
            if ipv6_addresses.get(ifname):
                sub["enabled_afi"] += ["IPv6"]
                sub["ipv6_addresses"] = [ipv6_addresses.get(ifname)]
            if description:
                sub["description"] = description
            if ifname in vrrp:
                sub["enabled_protocols"] += ["VRRP"]
            if "." in ifname:
                name, vlan_ids = ifname.split(".")
                sub["vlan_ids"] = [vlan_ids]
                for i in interfaces:
                    if i["name"] == name:
                        i["subinterfaces"] += [sub]
                        break
                continue
            typ = self.types[ifname[:2]]
            iface = {
                "name": ifname,
                "type": typ,
                "admin_status": astate == "Up",
                "oper_status": lstate == "Up",
                "mac": mac,
                "enabled_protocols": ["NDP"],
                "subinterfaces": [sub],
            }
            if description:
                iface["description"] = description
            if ifname in stp:
                iface["enabled_protocols"] += ["STP"]
            interfaces += [iface]
        return [{"interfaces": interfaces}]

    def clean_iftype(self, ifname, ifindex):
        iftype = self.snmp.get(mib["IF-MIB::ifType.%s" % ifindex], cached=True)
        return self.profile.get_interface_type(iftype)
