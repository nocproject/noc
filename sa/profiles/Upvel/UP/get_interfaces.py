# ---------------------------------------------------------------------
# Upvel.UP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Upvel.UP.get_interfaces"
    interface = IGetInterfaces

    rx_stp = re.compile(r"^(?P<port>(?:Gi|2.5G|10G) \S+)\s+", re.MULTILINE)
    rx_ctp = re.compile(
        r"^(?P<port>(?:Gi|2.5G|10G)\S+ \S+)\s*\n^\-+\s*\n^\s+Loop protect mode is enabled",
        re.MULTILINE,
    )
    rx_oam = re.compile(
        r"^(?P<port>(?:Gi|2.5G|10G)\S+)\s+(?P<port_num>\S+)\s+enabled", re.MULTILINE
    )
    rx_switchport = re.compile(
        r"^Name: (?P<port>(?:Gi|2.5G|10G)\S+ \S+)\s*\n"
        r"^Administrative mode: (?P<mode>\S+)\s*\n"
        r"^Access Mode VLAN: (?P<access_vlan>\d+)\s*\n"
        r"^Trunk Native Mode VLAN: (?P<native_vlan>\d+)\s*\n"
        r"^Administrative Native VLAN tagging: \S+\s*\n"
        r"(^VLAN Trunking: \S+\s*\n)?"
        r"^Allowed VLANs:(?P<vlans>.*)\n",
        re.MULTILINE,
    )
    rx_vlan = re.compile(r"^\s*(?:VLAN )?(?P<vlan>\d+)\s+", re.MULTILINE)
    rx_hybrid_vlan = re.compile(r"^Hybrid Native Mode VLAN: (?P<native_vlan>\d+)", re.MULTILINE)
    rx_link = re.compile(
        r"^\s*LINK: (?P<mac>\S+) Mtu:(?P<mtu>\d+) \<(?P<options>.+?)\>", re.MULTILINE
    )
    rx_ipv4 = re.compile(r"^\s+IPv4:\s+(?P<ip>\S+)", re.MULTILINE)
    rx_ipv6 = re.compile(r"^\s+IPv6:\s+(?P<ip>\S+)", re.MULTILINE)

    def get_gvrp(self):
        """
        Do not works !!! Need mor examples !!!

        try:
            v = self.cli("show gvrp protocol-state interface *")
            if "GVRP Feature is currently Disabled" not in v:
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        """
        return []

    def get_stp(self):
        try:
            r = []
            v = self.cli("show spanning-tree", cached=True)
            for match in self.rx_stp.finditer(v):
                r += [self.profile.convert_interface_name(match.group("port"))]
            return r
        except self.CLISyntaxError:
            return []

    def get_ctp(self):
        try:
            v = self.cli("show loop-protect")
            if "Loop Protection   : Enable" in v:
                return self.rx_ctp.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_oam(self):
        try:
            r = []
            v = self.cli("show link-oam", cached=True)
            for match in self.rx_oam.finditer(v):
                r += [match.group("port") + " " + match.group("port_num")]
            return r
        except self.CLISyntaxError:
            return []
        return []

    def execute_cli(self):
        interfaces = []
        gvrp = self.get_gvrp()
        stp = self.get_stp()
        ctp = self.get_ctp()
        oam = self.get_oam()
        snmp_indexes = []
        v = self.cli("show snmp mib ifmib ifIndex")
        for row in parse_table(v, max_width=80):
            snmp_indexes += [
                {
                    "ifindex": int(row[0].strip()),
                    "ifdescr": row[1].strip(),
                    "ifname": row[2].strip(),
                }
            ]
        v = self.cli("show interface * status", cached=True)
        for i in parse_table(v):
            ifname = i[0]
            admin_status = i[1] == "enabled"
            oper_status = i[6] != "Down"
            iface = {
                "name": ifname,
                "type": "physical",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            if ifname in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
            if ifname in stp:
                iface["enabled_protocols"] += ["STP"]
            if ifname in ctp:
                iface["enabled_protocols"] += ["CTP"]
            if ifname in oam:
                iface["enabled_protocols"] += ["OAM"]
            # Always enabled
            iface["enabled_protocols"] += ["LLDP"]
            for i in snmp_indexes:
                if ifname == i["ifname"]:
                    iface["snmp_ifindex"] = i["ifindex"]
                    iface["description"] = i["ifdescr"]
                    break
            sub = {
                "name": ifname,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "enabled_afi": ["BRIDGE"],
                "tagged_vlans": [],
            }
            s = self.cli("show interface %s switchport" % ifname)
            match1 = self.rx_switchport.search(s)
            if match1.group("mode") == "access":
                sub["untagged_vlan"] = int(match1.group("access_vlan"))
            elif match1.group("mode") == "trunk":
                sub["untagged_vlan"] = int(match1.group("native_vlan"))
                sub["tagged_vlans"] = self.expand_rangelist(match1.group("vlans").strip())
            elif match1.group("mode") == "hybrid":
                sub["untagged_vlan"] = int(match1.group("native_vlan"))
                sub["tagged_vlans"] = self.expand_rangelist(match1.group("vlans").strip())
                match2 = self.rx_hybrid_vlan.search(s)
                if match2:
                    sub["untagged_vlan"] = int(match2.group("native_vlan"))
            else:
                raise self.NotSupportedError()
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        v = self.cli("show ip interface brief")
        for match in self.rx_vlan.finditer(v):
            vlan_id = match.group("vlan")
            ll = self.cli("show interface vlan %s" % vlan_id)
            ifname = "VLAN%s" % vlan_id
            match1 = self.rx_link.search(ll)
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": True,
                "oper_status": "UP " in match1.group("options"),
                "mac": match1.group("mac"),
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": "UP " in match1.group("options"),
                        "mtu": match1.group("mtu"),
                        "mac": match1.group("mac"),
                        "enabled_afi": [],
                        "vlan_ids": [int(vlan_id)],
                    }
                ],
            }
            match1 = self.rx_ipv4.search(ll)
            if match1:
                iface["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
                iface["subinterfaces"][0]["ipv4_addresses"] = [match1.group("ip")]
            match1 = self.rx_ipv6.search(ll)
            if match1:
                iface["subinterfaces"][0]["enabled_afi"] += ["IPv6"]
                iface["subinterfaces"][0]["ipv6_addresses"] = [match1.group("ip")]
            for i in snmp_indexes:
                if ifname.lower() == i["ifname"].replace(" ", ""):
                    iface["snmp_ifindex"] = i["ifindex"]
                    iface["description"] = i["ifdescr"]
                    break
            interfaces += [iface]
        return [{"interfaces": interfaces}]
