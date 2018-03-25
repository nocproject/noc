# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "SKS.SKS.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<oper_status>Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE)
    rx_port1 = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<admin_status>Up|Down)",
        re.MULTILINE | re.IGNORECASE)
    rx_descr = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+(?P<descr>.+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_vlan = re.compile(
        r"^\s+(?P<vlan_id>\d+)\s+\S+\s+(?P<type>Untagged|Tagged)\s+"
        r"(?P<membership>\S+)\s*\n", re.MULTILINE)
    rx_vlan_ipif = re.compile(
        r"^(?P<address>\S+)\s+vlan\s*(?P<vlan_id>\d+)\s+"
        r"(?:Static|DHCP)\s+Valid")
    rx_mac = re.compile(
        r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)
    rx_enabled = re.compile(
        r"^\s*(?P<port>(?:Gi|Te|Po)\S+)\s+Enabled",
        re.MULTILINE | re.IGNORECASE)
    rx_lldp = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+(?:Rx|Tx)",
        re.MULTILINE | re.IGNORECASE)
    rx_iface = re.compile(
        r"^(?P<ifname>\S+\d) is( administratively)? "
        r"(?P<admin_status>up|down), "
        r"line protocol is (?P<oper_status>up|down)\s*\n"
        r"^\s+Ifindex is (?P<snmp_ifindex>\d+).*\n"
        r"(^\s+Description: (?P<descr>.+?)\s*\n)?"
        r"^\s+Hardware is (?P<hardware>\S+)"
        r"(, [Aa]ddress is (?P<mac>\S+)\s*\(.+\))?\s*\n"
        r"(^\s+Interface address is (?P<ip>\S+)\s*\n)?"
        r"^\s+MTU (?P<mtu>\d+) bytes", re.MULTILINE)

    IFTYPES = {
        "100BASE-TX": "physical",
        "Giga-TX": "physical",
        "Giga-FX": "physical",
        "Giga-FX-SFP": "physical",
        "Giga-Combo-TX": "physical",
        "EtherSVI": "SVI",
        "Null": "null"
    }

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

    def get_old_sks(self, c):
        interfaces = []
        descr = []
        adm_status = []
        switchport_support = True
        gvrp = self.get_gvrp()
        stp = self.get_stp()
        ctp = self.get_ctp()
        lldp = self.get_lldp()
        for line in c.split("\n"):
            match = self.rx_descr.match(line.strip())
            if match:
                if match.group("port") == "Port":
                    continue
                descr += [match.groupdict()]
        for line in self.cli("show interfaces configuration").split("\n"):
            match = self.rx_port1.match(line.strip())
            if match:
                adm_status += [match.groupdict()]
        for match in self.rx_port.finditer(self.cli("show interfaces status")):
            ifname = match.group("port")
            if ifname.startswith("Po"):
                iftype = "aggregated"
            else:
                iftype = "physical"
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
                "subinterfaces": []
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
                "tagged_vlans": []
            }
            for i in descr:
                if ifname == i["port"]:
                    iface["description"] = i["descr"]
                    sub["description"] = i["descr"]
                    break
            if switchport_support:
                # 1.5.11.3 supported, but 1.5.3 is not supported "show interfaces switchport" command
                try:
                    s = self.cli("show interfaces switchport %s" % ifname)
                    for match1 in self.rx_vlan.finditer(s):
                        vlan_id = match1.group("vlan_id")
                        if match1.group("membership") == "System":
                            continue
                        if match1.group("type") == "Untagged":
                            sub["untagged_vlan"] = int(vlan_id)
                        else:
                            sub["tagged_vlans"] += [int(vlan_id)]
                except self.CLISyntaxError:
                    self.logger.info("Model not supported switchport information")
                    switchport_support = False
                    pass
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
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
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "mac": mac,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [match.group("address")],
                        "vlan_ids": [int(match.group("vlan_id"))]
                    }]
                }
                interfaces += [iface]
        # Not implemented
        """
        for l in self.cli("show ipv6 interface").split("\n"):
            continue
        """
        return interfaces

    def get_new_sks(self):
        interfaces = []
        for match in self.rx_iface.finditer(self.cli("show interface")):
            iface = {
                "name": match.group("ifname"),
                "type": self.IFTYPES[match.group("hardware")],
                "admin_status": match.group("admin_status") == "up",
                "oper_status": match.group("oper_status") == "up",
                "snmp_ifindex": match.group("snmp_ifindex"),
            }
            sub = {
                "name": match.group("ifname"),
                "admin_status": match.group("admin_status") == "up",
                "oper_status": match.group("oper_status") == "up",
                "mtu": match.group("mtu")
            }
            if iface["type"] == "physical":
                sub["enabled_afi"] = ["BRIDGE"]
                c = self.cli("show vlan interface %s" % iface["name"])
                t = parse_table(c, allow_wrap=True)
                for i in t:
                    if i[1] == "Access":
                        sub["untagged_vlan"] = int(i[4])
                    elif i[1] == "Trunk":
                        sub["untagged_vlan"] = int(i[2])
                        sub["tagged_vlans"] = self.expand_rangelist(i[3])
                    else:
                        # Need more examples
                        raise self.NotSupportedError()
            if iface["name"].startswith("VLAN"):
                sub["vlan_ids"] = [iface["name"][4:]]
            if match.group("descr"):
                iface["description"] = match.group("descr")
                sub["description"] = match.group("descr")
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("ip"):
                sub["ip_addresses"] = [match.group("ip")]
                sub["enabled_afi"] = ["IPv4"]
            iface["subinterfaces"] = [sub]
            interfaces += [iface]
        return interfaces

    def execute(self):
        try:
            c = self.cli("show interfaces description")
        except self.CLISyntaxError:
            c = None
        if c:
            interfaces = self.get_old_sks(c)
        else:
            interfaces = self.get_new_sks()
        return [{"interfaces": interfaces}]
