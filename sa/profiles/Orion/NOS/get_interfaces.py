# ---------------------------------------------------------------------
# Orion.NOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Orion.NOS.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)\s+", re.MULTILINE
    )
    rx_port_beta = re.compile(
        r"^\s*P(?P<port>\d+)\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)\s+"
        r"\S+\s+\S+\s+\S+\s+\S+\s+(?P<descr>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_port_a26 = re.compile(
        r"^\s*(?P<ifname>\S+) is (?P<admin_status>\S+), line protocol is (?P<oper_status>\S+)(, dev index is (?P<ifindex>\d+))?\s*\n"
        r"(^\s*\S+ is layer 2 port, alias name is (?P<descr>\S+), index is (?P<snmp_ifindex>\d+)\s*\n)?"
        r"(^\s*Device flag .+\n)?"
        r"(^\s*Time since last status change.+\n)?"
        r"(^\s*IPv4 address is:\s*\n)?"
        r"(^\s*(?P<address>\S+)\s+(?P<mask>\S+)\s+\(Primary\)\s*\n)?"
        r"(^\s*VRF Bind: .+\n)?"
        r"^\s*Hardware is \S+, (active is \S+, )?address is (?P<mac>\S+)\s*\n"
        r"(^\s*PVID is (?P<pvid>\S+)\s*\n)?"
        r"^\s*MTU (is )?(?P<mtu>\d+) bytes",
        re.MULTILINE,
    )
    rx_descr = re.compile(r"^(?P<port>\d+)(?P<descr>.+)$", re.MULTILINE)
    rx_switchport = re.compile(
        r"^Administrative Mode: (?P<mode>\S+)\s*\n"
        r"^Operational Mode: \S+\s*\n"
        r"^Access Mode VLAN: (?P<access_vlan>\d+)\s*\n"
        r"^Administrative Access Egress VLANs: \S+\s*\n"
        r"^Operational Access Egress VLANs: \S+\s*\n"
        r"^Trunk Native Mode VLAN: (?P<native_vlan>\d+)\s*\n"
        r"(^Trunk Native VLAN: \S+\s*\n)?"
        r"^Administrative Trunk Allowed VLANs: (?P<vlans>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_switchport_beta = re.compile(
        r"^Interface: port(?P<port>\d+)\s*\n"
        r"^Reject frame type: \S+\s*\n"
        r"^Administrative Mode: (?P<mode>\S+)\s*\n"
        r"^Operational Mode: \S+\s*\n"
        r"^Access Mode VLAN: (?P<access_vlan>\d+)\s*\n"
        r"^Administrative Access Egress VLANs:.*\n"
        r"^Operational Access Egress VLANs:.*\n"
        r"^Trunk Native Mode VLAN: (?P<native_vlan>\d+)\s*\n"
        r"^Administrative Trunk Allowed VLANs: (?P<vlans>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_switchport_a26 = re.compile(
        r"^(?P<ifname>\S+)\s*\n"
        r"^Type :\S+\s*\n"
        r"^Mode :(?P<mode>\S+)\s*\n"
        r"^Port VID :(?P<pvid>\d+)\s*\n"
        r"(^Trunk allowed Vlan: (?P<vlans>\d+\S+)\s*\n)?",
        re.MULTILINE,
    )

    rx_enabled = re.compile(r"^\s*P?(?P<port>\d+)\s+Ena", re.MULTILINE | re.IGNORECASE)
    # do not verified
    rx_oam = re.compile(r"^\s*P?(?P<port>\d+)operate", re.MULTILINE | re.IGNORECASE)
    rx_lldp = re.compile(r"^\s*P?(?P<port>(?!0)\d+)\s+\d+", re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(
        r"^\s*(?P<ifname>\S+)\s+(?P<ip_address>\S+)\s+(?P<ip_subnet>\S+)\s+"
        r"(?P<vlan_id>\d+)\s+(?P<admin_status>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_ip_beta = re.compile(
        r"^\s*(?P<ifname>\d+)\s+(?P<ip_address>\d\S+)\s+(?P<ip_subnet>\d\S+)\s+",
        re.MULTILINE,
    )
    rx_ip_beta_vlan = re.compile(
        r"^\s*(?P<ifname>\d+)\s+(?P<vlan_id>\d+)\s*\n",
        re.MULTILINE,
    )
    port_count = 0

    def get_gvrp(self):
        try:
            if self.is_beta:
                v = self.cli("show gvrp port-list 1-%d" % self.port_count)
            else:
                v = self.cli("show gvrp configuration")
            if "GVRP Global Admin State: Disable" not in v:
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_stp(self):
        # Need more examples
        return []
        # try:
        #     v = self.cli("show spanning-tree")
        #     return self.rx_enabled.findall(v)
        # except self.CLISyntaxError:
        #     return []

    def get_ctp(self):
        try:
            v = self.cli("show loopback-detection")
            if "Loopback detection: Disabled" not in v:
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_lldp(self):
        try:
            v = self.cli("show lldp statistic")
            if "LLDP is not enabled." not in v:
                # Need more examples
                if self.is_beta:
                    return self.rx_lldp.findall(v)
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_oam(self):
        try:
            # Need more examples
            if self.is_beta:
                v = self.cli("show extended-oam status port-list 1-%d" % self.port_count)
            else:
                v = self.cli("show extended-oam status")
            return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []

    def execute_cli(self):
        interfaces = []
        descr = []
        if self.is_a26:
            c = self.cli("show interface")
            for match in self.rx_port_a26.finditer(c):
                ifname = match.group("ifname")
                iface = {
                    "name": ifname,
                    "type": self.profile.get_interface_type(ifname),
                    "admin_status": "up" in match.group("admin_status"),
                    "oper_status": "up" in match.group("oper_status"),
                    "mtu": match.group("mtu"),
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": "up" in match.group("admin_status"),
                            "oper_status": "up" in match.group("oper_status"),
                            "enabled_afi": [],
                        }
                    ],
                }
                if match.group("snmp_ifindex"):
                    iface["snmp_ifindex"] = match.group("snmp_ifindex")
                if match.group("ifindex"):
                    iface["snmp_ifindex"] = match.group("ifindex")
                if match.group("mac"):
                    iface["mac"] = match.group("mac")
                if match.group("descr") and match.group("descr") != "(null)":
                    iface["description"] = match.group("descr")
                if match.group("mac"):
                    iface["subinterfaces"][0]["untagged_vlan"] = match.group("pvid")
                if iface["type"] == "physical":
                    iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
                if iface["type"] == "SVI":
                    iface["subinterfaces"][0]["vlan_ids"] = ifname[4:]
                if match.group("address") and match.group("mask"):
                    ip_address = match.group("address")
                    ip_subnet = match.group("mask")
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                    iface["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
                    iface["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                interfaces += [iface]
            c = self.cli("show switchport interface")
            for match in self.rx_switchport_a26.finditer(c):
                ifname = match.group("ifname")
                for iface in interfaces:
                    if iface["name"] == ifname:
                        sub = iface["subinterfaces"][0]
                        if match.group("mode") == "Access":
                            sub["untagged_vlan"] = int(match.group("pvid"))
                        elif match.group("mode") == "Trunk":
                            sub["untagged_vlan"] = int(match.group("pvid"))
                            sub["tagged_vlans"] = self.expand_rangelist(
                                match.group("vlans").replace(";", ",")
                            )
                        else:
                            raise self.NotSupportedError()
                        break
            return [{"interfaces": interfaces}]

        if self.is_beta:
            self.port_count = self.profile.get_port_count(self)
        gvrp = self.get_gvrp()
        stp = self.get_stp()
        ctp = self.get_ctp()
        lldp = self.get_lldp()
        oam = self.get_oam()

        if self.is_beta:
            c = self.cli(("show interface port-list 1-%d" % self.port_count), cached=True)
            for match in self.rx_port_beta.finditer(c):
                ifname = match.group("port")
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": "enable" in match.group("admin_status"),
                    "oper_status": "down" not in match.group("oper_status"),
                    "enabled_protocols": [],
                    "snmp_ifindex": ifname,
                    "description": match.group("descr"),
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": "enable" in match.group("admin_status"),
                            "oper_status": "down" not in match.group("oper_status"),
                            "enabled_afi": ["BRIDGE"],
                        }
                    ],
                }
                if ifname in gvrp:
                    iface["enabled_protocols"] += ["GVRP"]
                if ifname in stp:
                    iface["enabled_protocols"] += ["STP"]
                if ifname in ctp:
                    iface["enabled_protocols"] += ["CTP"]
                if ifname in lldp:
                    iface["enabled_protocols"] += ["LLDP"]
                if ifname in oam:
                    iface["enabled_protocols"] += ["OAM"]
                interfaces += [iface]
            c = self.cli(("show interface port-list 1-%d switchport" % self.port_count))
            for match in self.rx_switchport_beta.finditer(c):
                ifname = match.group("port")
                for iface in interfaces:
                    if iface["name"] == ifname:
                        sub = iface["subinterfaces"][0]
                        if match.group("mode") == "access":
                            sub["untagged_vlan"] = int(match.group("access_vlan"))
                        elif match.group("mode") == "trunk":
                            sub["untagged_vlan"] = int(match.group("native_vlan"))
                            sub["tagged_vlans"] = self.expand_rangelist(match.group("vlans"))
                        else:
                            raise self.NotSupportedError()
                        break
            mac = self.scripts.get_chassis_id()[0].get("first_chassis_mac")
            c = self.cli("show interface ip")
            for match in self.rx_ip_beta.finditer(c):
                ip_address = match.group("ip_address")
                ip_subnet = match.group("ip_subnet")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                ifname = match.group("ifname")
                iface = {
                    "name": "ip%s" % ifname,
                    "type": "SVI",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": mac,
                    "subinterfaces": [
                        {
                            "name": "ip%s" % ifname,
                            "admin_status": True,
                            "oper_status": True,
                            "mac": mac,
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [ip_address],
                        }
                    ],
                }
                interfaces += [iface]
            c = self.cli("show interface ip vlan")
            for match in self.rx_ip_beta_vlan.finditer(c):
                ifname = "ip%s" % match.group("ifname")
                vid = match.group("vlan_id")
                for iface in interfaces:
                    if iface["name"] == ifname:
                        sub = iface["subinterfaces"][0]
                        sub["vlan_ids"] = vid
                        break
            # Not implemented
            # c = self.cli("show interface ipv6")
            return [{"interfaces": interfaces}]

        for line in self.cli("show interface port description").split("\n"):
            match = self.rx_descr.match(line.strip())
            if match:
                if match.group("port") == "Port":
                    continue
                descr += [match.groupdict()]
        for match in self.rx_port.finditer(self.cli("show interface port")):
            ifname = match.group("port")
            iface = {
                "name": ifname,
                "type": "physical",
                "admin_status": "enable" in match.group("admin_status"),
                "oper_status": match.group("oper_status") != "down",
                "enabled_protocols": [],
                "snmp_ifindex": ifname,
                "subinterfaces": [],
            }
            if ifname in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
            if ifname in stp:
                iface["enabled_protocols"] += ["STP"]
            if ifname in ctp:
                iface["enabled_protocols"] += ["CTP"]
            if ifname in lldp:
                iface["enabled_protocols"] += ["LLDP"]
            if ifname in oam:
                iface["enabled_protocols"] += ["OAM"]
            sub = {
                "name": ifname,
                "admin_status": "enable" in match.group("admin_status"),
                "oper_status": match.group("oper_status") == "!=",
                "enabled_afi": ["BRIDGE"],
                "tagged_vlans": [],
            }
            for i in descr:
                if ifname == i["port"]:
                    iface["description"] = i["descr"].strip()
                    sub["description"] = i["descr"].strip()
                    break
            s = self.cli("show interface port %s switchport" % ifname)
            match1 = self.rx_switchport.search(s)
            if match1.group("mode") == "access":
                sub["untagged_vlan"] = int(match1.group("access_vlan"))
            elif match1.group("mode") == "trunk":
                sub["untagged_vlan"] = int(match1.group("native_vlan"))
                sub["tagged_vlans"] = self.expand_rangelist(match1.group("vlans"))
            else:
                raise self.NotSupportedError()
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        mac = self.profile.get_version(self)["mac"]
        descr = []
        for line in self.cli("show interface ip description").split("\n"):
            match = self.rx_descr.match(line.strip())
            if match:
                if match.group("port") == "Port":
                    continue
                descr += [match.groupdict()]

        v = self.cli("show interface ip")
        for match in self.rx_ip.finditer(v):
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            ifname = match.group("ifname")
            iface = {
                "name": "ip%s" % ifname,
                "type": "SVI",
                "admin_status": match.group("admin_status") == "active",
                "oper_status": match.group("admin_status") == "active",
                "mac": mac,
                "subinterfaces": [
                    {
                        "name": "ip%s" % ifname,
                        "admin_status": match.group("admin_status") == "active",
                        "oper_status": match.group("admin_status") == "active",
                        "mac": mac,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [ip_address],
                        "vlan_ids": [int(match.group("vlan_id"))],
                    }
                ],
            }
            for i in descr:
                if ifname == i["port"]:
                    iface["description"] = i["descr"].strip()
                    iface["subinterfaces"][0]["description"] = i["descr"].strip()
                    break
            interfaces += [iface]
            # Not implemented
            # v = self.cli("show interface ipv6")
        return [{"interfaces": interfaces}]
