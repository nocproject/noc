# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.7302.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Alcatel.7302.get_interfaces"
    interface = IGetInterfaces

    rx_ifname = re.compile("port : (?P<ifname>\S+)")
    rx_ifindex = re.compile("if-index : (?P<ifindex>\d+)")
    rx_ififo = re.compile("info : \"(?P<info>.+?)\"")
    rx_type = re.compile("type : (?P<type>\S+)")
    rx_mac = re.compile("phy-addr : (?P<mac>\S+)")
    rx_admin_status = re.compile("admin-status : (?P<admin_status>up|down|not-appl)")
    rx_oper_status = re.compile("opr-status : (?P<oper_status>up|down)")
    rx_mtu = re.compile("largest-pkt-size : (?P<mtu>\d+)")
    rx_vpi_vci = re.compile("(?P<ifname>\S+\d+):(?P<vpi>\d+):(?P<vci>\d+)")
    rx_ip = re.compile(
        "^(?P<iface>\d+)\s+(?P<vlan_id>\d+)\s+(?P<admin_status>up|down)\s+"
        "(?P<oper_status>up|down)\s+(?P<ip>\d\S+)\s+(?P<mask>\d\S+)",
        re.MULTILINE)
    rx_mgmt_ip = re.compile(
        "host-ip-address manual:(?P<ip>\d+\.\d+\.\d+\.\d+\/\d+)")
    rx_mgmt_vlan = re.compile("mgnt-vlan-id (?P<vlan_id>\d+)")

    types = {
        "ethernet": "physical",
        "slip": "tunnel",
        "xdsl-line": "physical",
        "xdsl-channel": "physical",
        "atm-bonding": "physical",
        "atm": "physical",
        "atm-ima": "physical",
        "shdsl": "physical",
        "l2-vlan": "SVI",
        "sw-loopback": "loopback",
        "bonding": "other",
        "bridge-port": "other"
    }

    def execute(self):
        interfaces = []
        try:
            self.cli("environment inhibit-alarms mode batch terminal-timeout timeout:360")
        except self.CLISyntaxError:
            pass
        v = self.cli("show interface port detail")
        for p in v.split("----\nport\n----"):
            match = self.rx_ifname.search(p)
            if not match:
                continue
            ifname = match.group("ifname")
            match = self.rx_admin_status.search(p)
            admin_status = match.group("admin_status") == "up"
            match = self.rx_oper_status.search(p)
            oper_status = match.group("oper_status") == "up"
            match = self.rx_vpi_vci.search(ifname)
            if not match:
                match = self.rx_type.search(p)
                iftype = self.types[match.group("type")]
                match = self.rx_ifindex.search(p)
                ifindex = match.group("ifindex")
                i = {
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "type": iftype,
                    "snmp_ifindex": int(ifindex),
                    "enabled_protocols": [],
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": []
                    }],
                }
                match = self.rx_mac.search(p)
                if match:
                    i["mac"] = match.group("mac")
                    i["subinterfaces"][0]["mac"] = match.group("mac")
                match = self.rx_mtu.search(p)
                if match and int(match.group("mtu")) > 0:
                    i["subinterfaces"][0]["mtu"] = match.group("mtu")
                if iftype != "tunnel":
                    i["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
                if i["name"].startswith("l2-vlan:"):
                    i["subinterfaces"][0]["vlan_ids"] = [int(i["name"][8:])]
                interfaces += [i]
            else:
                vpi = match.group("vpi")
                vci = match.group("vci")
                sub = {
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "enabled_afi": ["BRIDGE", "ATM"],
                    "vpi": vpi,
                    "vci": vci
                }
                ifname = match.group("ifname").replace("atm-pvc", "atm-if")
                for i in interfaces:
                    if i["name"] == ifname:
                        i["subinterfaces"] += [sub]
                        break

        for match in self.rx_ip.finditer(self.cli("show ip shub vrf")):
            ip_address = match.group("ip")
            ip_subnet = match.group("mask")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i = {
                "name": match.group("iface"),
                "admin_status": match.group("admin_status") == "up",
                "oper_status": match.group("oper_status") == "up",
                "type": "SVI",
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": match.group("iface"),
                    "admin_status": match.group("admin_status") == "up",
                    "oper_status": match.group("oper_status") == "up",
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": [int(match.group("vlan_id"))]
                }]
            }
            interfaces += [i]
        v = self.cli("info configure system flat")
        match = self.rx_mgmt_ip.search(v)
        if match:
            i = {
                "name": "mgmt",
                "type": "management",
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": "mgmt",
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [match.group("ip")]
                }]
            }
            match = self.rx_mgmt_vlan.search(v)
            if match:
                i["subinterfaces"][0]["vlan_ids"] = \
                    [int(match.group("vlan_id"))]
            interfaces += [i]
        return [{"interfaces": interfaces}]
