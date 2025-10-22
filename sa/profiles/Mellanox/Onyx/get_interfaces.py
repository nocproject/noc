# ----------------------------------------------------------------------
# Mellanox.Onyx.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.validators import is_int, is_mac, is_ipv6_prefix


class Script(BaseScript):
    name = "Mellanox.Onyx.get_interfaces"
    interface = IGetInterfaces

    rx_vrf = re.compile(r"^\s+Name: (?P<vrf>\S+)\s*\n", re.MULTILINE)
    rx_iface = re.compile(
        r"^(?P<ifname>Eth\S+):\s*\n"
        r"^\s+Admin state\s+: (?P<admin_state>\S+)\s*\n"
        r"^\s+Operational state\s+: (?P<oper_state>\S+)\s*\n"
        r"^\s+Last change in operational status: .+\n"
        r"^\s+Boot delay time\s+: \d+ sec\s*\n"
        r"^\s+Description\s+: (?P<description>.*)\n"
        r"^\s+Mac address\s+: (?P<mac>\S+)\s*\n"
        r"^\s+MTU\s+: (?P<mtu>\d+)",
        re.MULTILINE,
    )
    rx_iface2 = re.compile(
        r"^Interface (?P<ifname>\S+) status:\s*\n"
        r"^\s+Comment\s+: (?P<description>.*)\n"
        r"(^\s+VRF\s+: (?P<vrf>\S+)\n)?"
        r"^\s+Admin up\s+: (?P<admin_state>.+)\s*\n"
        r"^\s+Link up\s+: (?P<oper_state>.+)\s*\n"
        r"^\s+DHCP running\s+: \S+\s*\n"
        r"^\s+IP address\s+:(?P<ip>.*)\n"
        r"^\s+Netmask\s+:(?P<mask>.*)\n"
        r"^\s+IPv6 enabled\s+: (?P<ipv6_enable>\S+)\n",
        re.MULTILINE,
    )
    rx_iface3 = re.compile(
        r"^\s+IPv6 address:\s*\n^\s+\S+",
        re.MULTILINE,
    )
    rx_iface4 = re.compile(
        r"^\s+MTU\s+: (?P<mtu>\d+)\s*\n^\s+HW address\s+: (?P<mac>\S+)",
        re.MULTILINE,
    )
    rx_switchport = re.compile(
        r"(?P<ifname>Eth\d\S+)\s+(?P<mode>trunk|access)\s+(?P<pvid>\d+|N/A)(\s+(?P<vlans>\S+))?"
    )
    rx_ip = re.compile(
        r"^(?P<ifname>Vlan \d+):\s*\n"
        r"^\s+Admin state\s+: (?P<admin_state>\S+)\s*\n"
        r"^\s+Operational state: (?P<oper_state>\S+)\s*\n"
        r"^\s+Autostate\s+: \S+\s*\n"
        r"^\s+Mac Address\s+: (?P<mac>\S+)\s*\n"
        r"^\s+DHCP client\s+: \S+\s*\n"
        r"^\s+PBR route-map\s+: .+\n"
        r"^\s*\n"
        r"^\s+IPv4 address:\s*\n"
        r"^\s+(?P<ip>\d\S+) \[primary\]\s*\n"
        r"^\s*\n"
        r"^\s+Broadcast address:\s*\n"
        r"^\s+.+\n"
        r"^\s*\n"
        r"^\s+MTU\s+: (?P<mtu>\d+) bytes",
        re.MULTILINE,
    )

    def execute_cli(self):
        vrfs = [
            {
                "forwarding_instance": "default",
                "type": "table",
                "interfaces": [],
            }
        ]
        c = self.cli("show vrf")
        for match in self.rx_vrf.finditer(c):
            if match.group("vrf") != "default":
                vrfs += [
                    {
                        "forwarding_instance": match.group("vrf"),
                        "type": "VRF",
                        "interfaces": [],
                    }
                ]
        vrf_name = ""
        c = self.cli("show interfaces", cached=True)
        for item in c.split("\n\n"):
            match = self.rx_iface.search(item)
            if match:
                iface = {
                    "name": match.group("ifname"),
                    "type": "physical",
                    "admin_status": match.group("admin_state") == "Enabled",
                    "oper_status": match.group("oper_state") == "Up",
                    "mac": match.group("mac"),
                    "subinterfaces": [
                        {
                            "name": match.group("ifname"),
                            "admin_status": match.group("admin_state") == "Enabled",
                            "oper_status": match.group("oper_state") == "Up",
                            "mac": match.group("mac"),
                            "mtu": match.group("mtu"),
                            "enabled_afi": ["BRIDGE"],
                        }
                    ],
                }
                if match.group("description").strip() != "N/A":
                    iface["description"] = match.group("description").strip()
                vrfs[0]["interfaces"] += [iface]
            else:
                match = self.rx_iface2.search(item)
                if match:
                    iface = {
                        "name": match.group("ifname"),
                        "admin_status": match.group("admin_state") == "yes",
                        "oper_status": match.group("oper_state") == "yes",
                        "subinterfaces": [
                            {
                                "name": match.group("ifname"),
                                "admin_status": match.group("admin_state") == "yes",
                                "oper_status": match.group("oper_state") == "yes",
                            }
                        ],
                    }
                    if match.group("ifname").startswith("lo"):
                        iface["type"] = "loopback"
                    elif match.group("ifname").startswith("mgmt"):
                        iface["type"] = "management"
                    if match.group("ip").strip():
                        iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
                        ip = match.group("ip").strip()
                        mask = match.group("mask")
                        ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
                        iface["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                    if match.group("ipv6_enable") == "yes":
                        if "enabled_afi" in iface["subinterfaces"][0]:
                            iface["subinterfaces"][0]["enabled_afi"] += ["IPv6"]
                        else:
                            iface["subinterfaces"][0]["enabled_afi"] = ["IPv6"]
                    if match.group("vrf"):
                        vrf_name = match.group("vrf")
                    else:
                        vrf_name = ""
                match = self.rx_iface3.search(item)
                if match and "IPv6" in iface["subinterfaces"][0]["enabled_afi"]:
                    iface["subinterfaces"][0]["ipv6_addresses"] = []
                    for line in item.splitlines():
                        if is_ipv6_prefix(line.strip()):
                            iface["subinterfaces"][0]["ipv6_addresses"] += [line.strip()]
                match = self.rx_iface4.search(item)
                if match:
                    iface["subinterfaces"][0]["mtu"] = match.group("mtu")
                    if is_mac(match.group("mac")):
                        iface["mac"] = match.group("mac")
                        iface["subinterfaces"][0]["mac"] = match.group("mac")
                    if vrf_name:
                        for vrf in vrfs:
                            if vrf["forwarding_instance"] == vrf_name:
                                vrf["interfaces"] += [iface]
                                break
                    else:
                        vrfs[0]["interfaces"] += [iface]
        c = self.cli("show interfaces switchport")
        for line in c.splitlines():
            match = self.rx_switchport.search(line)
            if match:
                ifname = match.group("ifname")
                for iface in vrfs[0]["interfaces"]:
                    if iface["name"] == ifname:
                        sub = iface["subinterfaces"][0]
                        if is_int(match.group("pvid")):
                            sub["untagged_vlan"] = match.group("pvid")
                        if match.group("vlans"):
                            sub["tagged_vlans"] = self.expand_rangelist(match.group("vlans"))
                        break

        c = self.cli("show ip interface")
        for match in self.rx_ip.finditer(c):
            iface = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": match.group("admin_state") == "Enabled",
                "oper_status": match.group("oper_state") == "Up",
                "mac": match.group("mac"),
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "admin_status": match.group("admin_state") == "Enabled",
                        "oper_status": match.group("oper_state") == "Up",
                        "mac": match.group("mac"),
                        "mtu": match.group("mtu"),
                        "enabled_afi": ["IPv4"],
                        "ipv4_addesses": [match.group("ip")],
                        "vlan_ids": match.group("ifname")[5:],
                    }
                ],
            }
            vrfs[0]["interfaces"] += [iface]

        return vrfs
