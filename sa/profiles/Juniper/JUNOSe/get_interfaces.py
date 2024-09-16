# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_interfases
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import copy

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Juniper.JUNOSe.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 360

    rx_conf_iface = re.compile(r"interface (?P<iftype>\S+) (?P<ifname>\S+)")
    rx_iface = re.compile(
        r"^(?P<interface>\S+)\s+is\s+(?P<oper_status>Up|Down), "
        r"Administrative status is (?P<admin_status>Up|Down)\s*\n"
        r"(^\s*Description:(?P<descr>.*)\n)?"
        r"^\s*Hardware is .+, address is (?P<mac>\S+)\s*\n"
        r"^.+\n"
        r"(^.+\n)?"
        r"^\s*MTU: Operational (?P<mtu>\d+)",
        re.MULTILINE,
    )
    rx_iface1 = re.compile(
        r"^(?P<interface>\S+)\s+is\s+(?P<oper_status>Up|Down), "
        r"Administrative status is (?P<admin_status>Up|Down)\s*\n"
        r"^\s+VLAN ID: (?P<vlan_id>\d+)",
        re.MULTILINE,
    )
    rx_ipif = re.compile(
        r"^(?:TUNNEL )?(?P<interface>\S+) line protocol( (?P<l_proto>\S+))? is (?P<oper_status>up|down), "
        r"ip is (?P<admin_status>up|down)\s*\n"
        r"^\s+Description:(?P<descr>.*)\s*\n"
        r"^\s+Network Protocols: (?P<n_proto>.+)\s*\n"
        r"(^\s+Unnumbered Interface on (?P<unnumbered>\S+)\s*\n)?"
        r"(^\s+\( IP address  (?P<ip_address>\S+) \)\s*\n)?"
        r"(^\s+Internet address is (?P<ip>\S+)/(?P<mask>\S+)\s*\n)?"
        r"((?P<ip_secondary>(^\s+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ \(secondary\)\s*\n)*))?"
        r"(^\s+Broadcast address is (?P<broadcast>\S+)\s*\n)?"
        r"^\s+Operational MTU = (?P<mtu>\d+)  Administrative MTU = \d+\s*\n",
        re.MULTILINE,
    )
    rx_secondary = re.compile(r"^\s+(?P<ip>\S+)/(?P<mask>\S+) \(secondary\)\s*\n", re.MULTILINE)
    rx_vrfs = re.compile(r"^(?P<vrf>\S+)\s+(?P<rd>\d+:\d+)\s+\S+\s*\n", re.MULTILINE)
    phys_interfaces = []
    logical_interfaces = []

    def get_ifaces(self, vrf):
        ifaces = copy.deepcopy(self.phys_interfaces)
        changed = False
        for l_iface in self.logical_interfaces:
            if not self.profile.valid_interface_name(l_iface):
                continue
            if vrf == "default":
                v = self.cli("show ip interface %s" % l_iface)
            else:
                v = self.cli("show ip interface vrf %s %s" % (vrf, l_iface))
            match = self.rx_ipif.search(v)
            if match:
                ifname = match.group("interface")
                parent_iface = ifname
                iface = {
                    "name": ifname,
                    "admin_status": match.group("admin_status") == "Up",
                    "oper_status": match.group("oper_status") == "Up",
                    "enabled_protocols": [],
                }
                iftype = ""
                if match.group("l_proto") == "Ethernet":
                    iftype = "physical"
                elif match.group("l_proto") in ["Ppp", "IpTunnel"]:
                    iftype = "tunnel"
                if ifname.startswith("null"):
                    iftype = "null"
                elif ifname.startswith("loopback"):
                    iftype = "loopback"
                if iftype == "":
                    iftype = "unknown"
                iface["type"] = iftype
                sub = {
                    "name": ifname,
                    "admin_status": match.group("admin_status") == "Up",
                    "oper_status": match.group("oper_status") == "Up",
                    "mtu": match.group("mtu"),
                    "enabled_afi": ["IPv4"],
                    "enabled_protocols": [],
                }
                if "." in ifname:
                    parent_iface, vlan_tag = ifname.split(".")
                    sub["vlan_ids"] = [vlan_tag]
                if match.group("ip_address"):
                    sub["ipv4_addresses"] = [match.group("ip_address") + "/32"]
                if match.group("ip") and match.group("mask"):
                    ip_address = match.group("ip")
                    ip_subnet = match.group("mask")
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                    sub["ipv4_addresses"] = [ip_address]
                if match.group("ip_secondary"):
                    ip_secondary = match.group("ip_secondary")
                    for match1 in self.rx_secondary.finditer(ip_secondary):
                        ip_address = match1.group("ip")
                        ip_subnet = match1.group("mask")
                        ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                        sub["ipv4_addresses"] += [ip_address]
                if ", " in match.group("n_proto"):
                    # Need more examples
                    n_proto = match.group("n_proto").split(", ")
                    if "ISIS" in n_proto:
                        sub["enabled_protocols"] += ["ISIS"]
                    if "OSPF" in n_proto:
                        sub["enabled_protocols"] += ["OSPF"]
                    if "RSVP" in n_proto:
                        sub["enabled_protocols"] += ["RSVP"]
                    if "PIM" in n_proto:
                        sub["enabled_protocols"] += ["PIM"]
                    if "IGMP" in n_proto:
                        sub["enabled_protocols"] += ["IGMP"]
                    if "DVMRP" in n_proto:
                        sub["enabled_protocols"] += ["DVMRP"]
                if ifname.startswith("gre:"):
                    sub["tunnel"] = {}
                    sub["tunnel"]["type"] = "GRE"
                    if match.group("ip_address"):
                        sub["tunnel"]["local_address"] = match.group("ip_address")
                    elif match.group("ip"):
                        sub["tunnel"]["local_address"] = match.group("ip")
                if match.group("descr"):
                    descr = match.group("descr").strip()
                    iface["description"] = descr
                    sub["description"] = descr

                found = False
                for i in ifaces:
                    if i["name"] == parent_iface:
                        if i["subinterfaces"][0]["name"] != sub["name"]:
                            i["subinterfaces"] += [sub]
                        else:
                            sub["enabled_afi"] += i["subinterfaces"][0]["enabled_afi"]
                            sub["enabled_protocols"] += i["subinterfaces"][0]["enabled_protocols"]
                            i["subinterfaces"][0].update(sub)
                        found = True
                        changed = True
                        break
                if found:
                    continue
                iface["subinterfaces"] = [sub]
                ifaces += [iface]
                changed = True
            elif "." in l_iface:
                v = self.cli("show interface %s" % l_iface)
                match = self.rx_iface1.search(v)
                if match:
                    ifname = match.group("interface")
                    parent_iface, vlan_tag = ifname.split(".")
                    sub = {
                        "name": ifname,
                        "admin_status": match.group("admin_status") == "Up",
                        "oper_status": match.group("oper_status") == "Up",
                        "vlan_ids": [match.group("vlan_id")],
                    }
                    for i in ifaces:
                        if i["name"] == parent_iface:
                            if i["subinterfaces"][0]["name"] != sub["name"]:
                                i["subinterfaces"] += [sub]
                            else:
                                sub["enabled_afi"] += i["subinterfaces"][0]["enabled_afi"]
                                sub["enabled_protocols"] += i["subinterfaces"][0][
                                    "enabled_protocols"
                                ]
                                i["subinterfaces"][0].update(sub)
                            # Need more examples
                            # changed = True
                            break

        if changed:
            return ifaces
        else:
            return []

    def execute_cli(self, interface=None):
        v = self.cli("show running-configuration | include interface")
        for link in v.split("\n"):
            match = self.rx_conf_iface.match(link)
            if match:
                iface = match.group("iftype") + " " + match.group("ifname")
                if iface not in self.logical_interfaces:
                    self.logical_interfaces += [iface]
        for v in self.profile.get_interfaces_list(self):
            cmd = "show interface %s" % v
            c = self.cli(cmd)
            match = self.rx_iface.search(c)
            iface = {
                "name": match.group("interface"),
                "type": "physical",
                "admin_status": match.group("admin_status") == "Up",
                "oper_status": match.group("oper_status") == "Up",
                "mac": match.group("mac"),
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": match.group("interface"),
                        "admin_status": match.group("admin_status") == "Up",
                        "oper_status": match.group("oper_status") == "Up",
                        "mac": match.group("mac"),
                        "mtu": match.group("mtu"),
                        "enabled_afi": ["BRIDGE"],
                        "enabled_protocols": [],
                    }
                ],
            }
            if match.group("descr"):
                descr = match.group("descr").strip()
                iface["description"] = descr
                iface["subinterfaces"][0]["description"] = descr
            self.phys_interfaces += [iface]

        r = [
            {
                "forwarding_instance": "default",
                "type": "ip",
                "interfaces": self.get_ifaces("default"),
            }
        ]
        for match in self.rx_vrfs.finditer(self.cli("show ip vrf")):
            r += [
                {
                    "forwarding_instance": match.group("vrf"),
                    "type": "ip",
                    "rd": match.group("rd"),
                    "interfaces": self.get_ifaces(match.group("vrf")),
                }
            ]
        return r
