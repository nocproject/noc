# ---------------------------------------------------------------------
# Angtel.Topaz.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Angtel.Topaz.get_interfaces"
    interface = IGetInterfaces

    always_prefer = "S"

    rx_port = re.compile(
        r"^(?P<port>(?:Fa|Gi|Te|Po)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<oper_status>Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_port1 = re.compile(
        r"^(?P<port>(?:Fa|Gi|Te|Po)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<admin_status>Up|Down)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_descr = re.compile(
        r"^(?P<port>(?:Fa|Gi|Te|Po)\S+)\s+(?P<descr>.+)$", re.MULTILINE | re.IGNORECASE
    )
    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+\S+\s+(?P<type>Untagged|Tagged)\s+" r"(?P<membership>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlan_ipif = re.compile(
        r"^(?P<address>\S+)\s+vlan\s*(?P<vlan_id>\d+)\s+" r"(?:Static|DHCP)\s+Valid"
    )
    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)
    rx_enabled = re.compile(
        r"^\s*(?P<port>(?:Gi|Te|Po)\S+)\s+Enabled", re.MULTILINE | re.IGNORECASE
    )
    rx_lldp = re.compile(r"^(?P<port>(?:Fa|Gi|Te|Po)\S+)\s+(?:Rx|Tx)", re.MULTILINE | re.IGNORECASE)

    def get_gvrp(self):
        try:
            v = self.cli("show gvrp configuration")
            if "GVRP Feature is currently Disabled" not in v:
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_stp(self):
        try:
            v = self.cli("show spanning-tree")
            return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []

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
            v = self.cli("show lldp configuration")
            if "LLDP state: Enabled" in v:
                return self.rx_lldp.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def execute_cli(self):
        interfaces = []
        descr = []
        adm_status = []
        gvrp = self.get_gvrp()
        stp = self.get_stp()
        ctp = self.get_ctp()
        lldp = self.get_lldp()
        for line in self.cli("show interfaces description").split("\n"):
            match = self.rx_descr.match(line.strip())
            if match:
                if match.group("port") == "Port":
                    continue
                descr += [match.groupdict()]
        for line in self.cli("show interfaces configuration").split("\n"):
            match = self.rx_port1.match(line.strip())
            if match:
                adm_status += [match.groupdict()]
        for match in self.rx_port.finditer(self.cli("show interfaces status", cached=True)):
            ifname = match.group("port")
            iftype = self.profile.get_interface_type(ifname)
            for i in adm_status:
                if ifname == i["port"]:
                    st = bool(i["admin_status"] == "Up")
                    break
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": st,
                "oper_status": match.group("oper_status") == "Up",
                "enabled_protocols": [],
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
            sub = {
                "name": ifname,
                "admin_status": st,
                "oper_status": match.group("oper_status") == "Up",
                "enabled_afi": ["BRIDGE"],
                "tagged_vlans": [],
            }
            for i in descr:
                if ifname == i["port"]:
                    iface["description"] = i["descr"]
                    sub["description"] = i["descr"]
                    break
            s = self.cli("show interfaces switchport %s" % ifname)
            for match1 in self.rx_vlan.finditer(s):
                vlan_id = match1.group("vlan_id")
                if match1.group("membership") == "System":
                    continue
                if match1.group("type") == "Untagged":
                    sub["untagged_vlan"] = int(vlan_id)
                else:
                    sub["tagged_vlans"] += [int(vlan_id)]
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        match = self.rx_mac.search(self.cli("show system", cached=True))
        mac = match.group("mac")
        for line in self.cli("show ip interface").split("\n"):
            match = self.rx_vlan_ipif.match(line.strip())
            if match:
                ifname = "vlan" + match.group("vlan_id")
                iface = {
                    "name": ifname,
                    "type": "SVI",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": mac,
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": True,
                            "oper_status": True,
                            "mac": mac,
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [match.group("address")],
                            "vlan_ids": [int(match.group("vlan_id"))],
                        }
                    ],
                }
                interfaces += [iface]
        # Not implemented
        """
        for l in self.cli("show ipv6 interface").split("\n"):
            continue
        """
        return [{"interfaces": interfaces}]
