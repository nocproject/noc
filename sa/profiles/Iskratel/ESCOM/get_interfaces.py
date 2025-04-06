# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_interfaces"
    interface = IGetInterfaces
    cache = True

    rx_port = re.compile(
        r"^(?P<port>(?:Gi|Te|Po|oo)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<oper_status>Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_port1 = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+" r"(?P<admin_status>Up|Down)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_descr = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+(?P<descr>.+)$", re.MULTILINE | re.IGNORECASE
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
    rx_lldp = re.compile(r"^(?P<port>(?:Gi|Te|Po)\S+)\s+(?:Rx|Tx)", re.MULTILINE | re.IGNORECASE)
    rx_iface = re.compile(
        r"^Port type: ethernet-csmacd, MTU: (?P<mtu>\d+)\s*\n"
        r"^Physically address: (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_escom_l_port = re.compile(
        r"(?P<name>\S+)\s+is (administratively |)(?P<admin_status>\S+), line protocol is (?P<oper_status>\S+)\n\s+Ifindex is (?P<ifindex>\d+).*(,\s*unique port number is (?P<unique_port>\d+?))?\n\s+(Description:\s+(?P<description>\S+)\n\s+|)Hardware is (?P<type>\S+), [Aa]ddress is (?P<mac>\S+)\s*(\(.+\))?(\n\s+Interface address is (?P<address>\S+)|)\n\s+MTU\s+(?P<mtu>\d+)?",
        re.MULTILINE,
    )

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

    def get_escom_l_vlans(self):
        r = {}
        v = self.cli("show vlan")
        for vid, vtype, vname, ifaces in parse_table(v, allow_wrap=True, n_row_delim=", "):
            if not ifaces.strip():
                continue
            for iface in ifaces.split(","):
                iface = self.profile.convert_interface_name(iface.strip())
                if iface not in r:
                    r[iface] = {"tagged": []}
                r[iface]["tagged"] += [int(vid)]
        return r

    rx_split_mac = re.compile(r"(?P<mac>\S+)\((bia |)\S+\)")

    def execute_escom_l(self):
        interfaces = {}
        switchport = self.get_escom_l_vlans()
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        v = self.cli("show interface")
        for iface in self.rx_escom_l_port.finditer(v):
            ifname = self.profile.convert_interface_name(iface.group("name"))
            iftype = self.profile.get_interface_type(ifname)
            interfaces[ifname] = {
                "type": iftype,
                "name": ifname,
                "snmp_ifindex": iface.group("ifindex"),
                "admin_status": iface.group("admin_status") == "up",
                "oper_status": iface.group("oper_status") == "up",
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            if ifname in switchport:
                interfaces[ifname]["subinterfaces"] += [
                    {
                        "name": ifname,
                        "admin_status": iface.group("admin_status") == "up",
                        "oper_status": iface.group("oper_status") == "up",
                        "enabled_afi": ["BRIDGE"],
                        "tagged_vlans": switchport[ifname]["tagged"],
                    }
                ]
            if iface.group("address"):
                interfaces[ifname]["subinterfaces"] += [
                    {
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        # "mac": mac,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [iface.group("address")],
                    }
                ]
            if iface.group("mac"):
                if self.rx_split_mac.match(iface.group("mac")):
                    interfaces[ifname]["mac"] = self.rx_split_mac.match(iface.group("mac")).group(
                        "mac"
                    )
                else:
                    interfaces[ifname]["mac"] = iface.group("mac")
            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                interfaces[ifname]["aggregated_interface"] = ai
                if is_lacp:
                    interfaces[ifname]["enabled_protocols"] += ["LACP"]
        return [{"interfaces": list(interfaces.values())}]

    def execute_cli(self, **kwargs):
        if self.is_escom_l:
            return self.execute_escom_l()
        interfaces = []
        descr = []
        adm_status = []
        gvrp = self.get_gvrp()
        stp = self.get_stp()
        ctp = self.get_ctp()
        lldp = self.get_lldp()
        for ll in self.cli("show interfaces description").split("\n"):
            match = self.rx_descr.match(ll.strip())
            if match:
                if match.group("port") == "Port":
                    continue
                descr += [match.groupdict()]
        for ll in self.cli("show interfaces configuration").split("\n"):
            match = self.rx_port1.match(ll.strip())
            if match:
                adm_status += [match.groupdict()]
        for match in self.rx_port.finditer(self.cli("show interfaces status")):
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
            try:
                s = self.cli("show interfaces %s" % ifname)
                match = self.rx_iface.search(s)
                if match:
                    iface["mac"] = match.group("mac")
                    sub["mac"] = match.group("mac")
                    sub["mtu"] = match.group("mtu")
            except self.CLISyntaxError:
                pass
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        for ll in self.cli("show ip interface").split("\n"):
            match = self.rx_vlan_ipif.match(ll.strip())
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
