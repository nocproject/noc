# ---------------------------------------------------------------------
# Iskratel.MSAN.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
from collections import defaultdict

# NOC modules
# from noc.core.script.base import BaseScript
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Iskratel.MSAN.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 240

    rx_if_pvc = re.compile(
        r"^Interface\.+ (?P<port>\S+).+?"
        r"^\s+PVC\n"
        r"^PVC\s+VLAN ID\n"
        r"^------- -------\n"
        r"^(?P<pvcs>(\d+/\d+\s+\d+\n)+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_pvc = re.compile(r"^(?P<vpi>\d+)/(?P<vci>\d+)\s+(?P<vlan>\d+)$", re.MULTILINE)
    rx_pvc1 = re.compile(r"^(?P<port>\d+/\d+/\d+)\s+(?P<vpi>\d+)/(?P<vci>\d+)$", re.MULTILINE)
    rx_svi = re.compile(
        r"^IP Address\.+ (?P<ip>\S+)\n"
        r"^Subnet Mask\.+ (?P<mask>\S+)\n"
        r"^Burned In MAC Address\.+ (?P<mac>\S+)\n"
        r"(^.+\n)?"
        r"(^.+\n)?"
        r"(^.+\n)?"
        r"^Management VLAN ID\.+ (?P<vlan>\d+)\n",
        re.MULTILINE,
    )
    rx_port = re.compile(
        r"^(?P<port>\d+/\d+)\s+(?:\s+|PC|PC Mbr)\s+"
        r"(?P<admin_status>Enable|Disable)\s+"
        r"(?:Auto|1000 Full|100 Full|100 Half|10 Full|10 Half)\s+"
        r"(?:\s+|Auto|1000 Full|100 Full|100 Half|10 Full|10 Half)\s+"
        r"(?P<oper_status>Up|Down)\s+(?:Enable|Disable)\s+"
        r"(?:Enable|Disable)(?P<descr>.*?)\n",
        re.MULTILINE,
    )
    rx_port1 = re.compile(r"(?P<port>\d+/\d+)/\d+")
    rx_port2 = re.compile(
        r"Interface\.+\S+\n"
        r"ifIndex\.+(?P<ifindex>\d+)\n"
        r"Description\.+(?P<descr>.*)\n"
        r"MAC Address\.+(?P<mac>\S+)\n",
        re.MULTILINE,
    )
    rx_port3 = re.compile(r"Interface\.+\S+\nDescription\.+(?P<descr>.*)\n", re.MULTILINE)
    rx_vlan = re.compile(r"^(?P<port>\d+/\d+/\d+)\s+(?P<vlan>\d+)\s+", re.MULTILINE)
    rx_vlan1 = re.compile(
        r"^(?P<port>\d+/\d+)\s+Include\s+Include\s+(?P<type>\S+)\s*\n", re.MULTILINE
    )

    def get_switchport_cli(self):
        result = defaultdict(lambda: {"tagged_vlans": [], "untagged_vlan": None})
        for v in self.scripts.get_vlans():
            c = self.cli("show vlan %s" % v["vlan_id"])
            for match in self.rx_vlan1.finditer(c):
                ifname = match.group("port")
                if match.group("type") == "Untagged":
                    result[ifname]["untagged_vlan"] = v["vlan_id"]
                if match.group("type") == "Tagged":
                    result[ifname]["tagged_vlans"] += [v["vlan_id"]]
        return result

    def execute_cli(self, **kwargs):
        pch = self.scripts.get_portchannel()
        switchports = self.get_switchport_cli()
        pvc = []
        if not self.is_switch_board:
            try:
                c = self.cli("show interface all pvc")
                for match in self.rx_if_pvc.finditer(c):
                    for match1 in self.rx_pvc.finditer(match.group("pvcs")):
                        pvc += [
                            {
                                "port": match.group("port"),
                                "vpi": int(match1.group("vpi")),
                                "vci": int(match1.group("vci")),
                                "vlan": int(match1.group("vlan")),
                            }
                        ]
            except self.CLISyntaxError:
                _ = self.cli("\x08" * 22)
                c = self.cli("show pvc all")
                for match in self.rx_pvc1.finditer(c):
                    pvc += [
                        {
                            "port": match.group("port"),
                            "vpi": int(match.group("vpi")),
                            "vci": int(match.group("vci")),
                        }
                    ]
                c = self.cli("show vlan port all")
                for match in self.rx_vlan.finditer(c):
                    ifname = match.group("port")
                    for p in pvc:
                        if p["port"] == ifname:
                            p["vlan"] = int(match.group("vlan"))
                            break
        interfaces = []
        for match in self.rx_port.finditer(self.cli("show port all")):
            ifname = match.group("port")
            i = {
                "name": ifname,
                "type": "physical",
                "admin_status": match.group("admin_status") == "Enable",
                "oper_status": match.group("oper_status") == "Up",
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            descr = match.group("descr").strip()
            if descr and not descr.startswith("Short ") and not descr.startswith("Long "):
                i["description"] = descr
            try:
                c = self.cli("show port description %s" % ifname)
                match1 = self.rx_port2.search(c)
                if match1:
                    i["snmp_ifindex"] = match1.group("ifindex")
                    i["mac"] = match1.group("mac")
                else:
                    match1 = self.rx_port3.search(c)
                if match1 and match1.group("descr"):
                    i["description"] = match1.group("descr")
            except self.CLISyntaxError:
                pass
            if pch:
                for p in pch:
                    if ifname == p["interface"]:
                        i["type"] = "aggregated"
                        break
                    if ifname in p["members"]:
                        i["aggregated_interface"] = p["interface"]
                        break
            if not i["subinterfaces"]:
                i["subinterfaces"] = [
                    {
                        "name": ifname,
                        "admin_status": match.group("admin_status") == "Enable",
                        "oper_status": match.group("oper_status") == "Up",
                        "enabled_afi": ["BRIDGE"],
                    }
                ]
                if "mac" in i:
                    i["subinterfaces"][0]["mac"] = i["mac"]
                if "description" in i:
                    i["subinterfaces"][0]["description"] = i["description"]
                if ifname in switchports:
                    i["subinterfaces"][0]["tagged_vlans"] = switchports[ifname]["tagged_vlans"]
                    i["subinterfaces"][0]["untagged_vlan"] = switchports[ifname]["untagged_vlan"]
            for p in pvc:
                match1 = self.rx_port1.search(p["port"])
                if p["port"] == ifname or (match1 and match1.group("port") == ifname):
                    s = {
                        "name": "%s-%s.%s" % (p["port"], p["vpi"], p["vci"]),
                        "admin_status": match.group("admin_status") == "Enable",
                        "oper_status": match.group("oper_status") == "Enable",
                        "vpi": p["vpi"],
                        "vci": p["vci"],
                        "enabled_afi": ["BRIDGE", "ATM"],
                    }
                    if "vlan" in p:
                        s["vlan_ids"] = p["vlan"]
                    i["subinterfaces"] += [s]
            interfaces += [i]
        match = self.rx_svi.search(self.cli("show network"))
        if match:
            i = {
                "name": "mgmt",
                "type": "SVI",
                "oper_status": True,
                "admin_status": True,
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": "mgmt",
                        "oper_status": True,
                        "admin_status": True,
                        "mac": match.group("mac"),
                        "vlan_ids": [int(match.group("vlan"))],
                        "enabled_afi": ["IPv4"],
                    }
                ],
            }
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            interfaces += [i]
        return [{"interfaces": interfaces}]
