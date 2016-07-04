# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5600T.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.ip import IPv4
import re


class Script(BaseScript):
    name = "Huawei.MA5600T.get_interfaces"
    interface = IGetInterfaces

    rx_if = re.compile(
        r"^\s*(?P<ifname>[a-zA-Z]+)(?P<ifnum>\d+) current state :\s*(?P<admin_status>UP|DOWN)\s*\n"
        r"^\s*Line protocol current state :\s*(?P<oper_status>UP|UP \(spoofing\)|DOWN)\s*\n"
        r"^\s*Description :\s*(?P<descr>.*)\n"
        r"^\s*The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"(^\s*Internet Address is (?P<ip>\S+)\s*\n)?"
        r"(^\s*IP Sending Frames' Format is PKTFMT_ETHNT_2, Hardware address is (?P<mac>\S+)\s*\n)?",
        re.MULTILINE)
    rx_vlan = re.compile(
        r"^\s*\-+\s*\n"
        r"(?P<tagged>.+)"
        r"^\s*\-+\s*\n"
        r"^\s*Total:\s+\d+\s+Native VLAN:\s+(?P<untagged>\d+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_tagged = re.compile("(?P<tagged>\d+)", re.MULTILINE)
    rx_ether = re.compile(
        r"^\s*(?P<port>\d+)\s+GE\s+\S+\s+\d+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<admin_status>\S+)\s+(?P<oper_status>\S+)\s*\n", re.MULTILINE)
    rx_adsl_state = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<oper_state>\S+)", re.MULTILINE)
    rx_pvc = re.compile(
        r"^\s*\d+\s+p2p\s+lan\s+0/\d+\s*/(?P<vlan>\d+)\s+\S*\s+\S+\s+\S+\s+"
        r"adl\s+0/\d+\s*/(?P<port>\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+\d+\s+"
        r"(?P<admin_status>\S+)\s*\n", re.MULTILINE)
    rx_sp = re.compile(
        r"^\s*\d+\s+(?P<vlan>\d+)\s+\S+\s+adl\s+0/\d+\s*/(?P<port>\d+)\s+"
        r"(?P<vpi>\d+)\s+(?P<vci>\d+)\s+\S+\s+\S+\s+\d+\s+\d+\s+"
        r"(?P<admin_status>up|down)\s*$", re.MULTILINE)

    def execute(self):
        interfaces = []
        vlans = []
        ports = self.profile.fill_ports(self)
        for i in range(len(ports)):
            if ports[i]["t"] == "GE":
                v = self.cli("display board 0/%d" % i)
                for match in self.rx_ether.finditer(v):
                    ifname = "0/%d/%d" % (i, int(match.group("port")))
                    admin_status = match.group("admin_status") == "active"
                    oper_status = match.group("oper_status") == "online"
                    v = self.cli("display port vlan %s" % ifname)
                    tagged = []
                    m = self.rx_vlan.search(v)
                    untagged = int(m.group("untagged"))
                    for t in self.rx_tagged.finditer(m.group("tagged")):
                        if int(t.group("tagged")) != untagged:
                            tagged += [int(t.group("tagged"))]
                    iface = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "subinterfaces": [{
                            "name": ifname,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "enabled_afi": ["BRIDGE"],
                            "untagged": untagged,
                            "tagged": tagged
                        }]
                    }
                    interfaces += [iface]
        for i in range(len(ports)):
            if ports[i]["t"] == "ADSL":
                oper_states = []
                v = self.cli("display adsl port state 0/%d\n" % i)
                for match in self.rx_adsl_state.finditer(v):
                    oper_states += [{
                        "name": "0/%d/%d" % (i, int(match.group("port"))),
                        "oper_state": match.group("oper_state") == "Activated"
                    }]
                try:
                    v = self.cli("display pvc 0/%d\n" % i)
                    rx_adsl = self.rx_pvc
                except self.CLISyntaxError:
                    v = self.cli("display service-port board 0/%d\n" % i)
                    rx_adsl = self.rx_sp
                for match in rx_adsl.finditer(v):
                    port = int(match.group("port"))
                    ifname = "0/%d/%d" % (i, port)
                    sub = {
                        "name": ifname,
                        "admin_status": match.group("admin_status") == "up",
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "vpi": int(match.group("vpi")),
                        "vci": int(match.group("vci")),
                        "vlan_ids": int(match.group("vlan"))
                    }
                    found = False
                    for iface in interfaces:
                        if ifname == iface["name"]:
                            iface["subinterfaces"] += [sub]
                            found = True
                            break
                    if not found:
                        iface = {
                            "name": ifname,
                            "type": "physical",
                            "subinterfaces": [sub]
                        }
                        for o in oper_states:
                            if ifname == o["name"]:
                                iface["oper_status"] = o["oper_state"]
                                break
                        interfaces += [iface]
        v = self.cli("display interface\n")
        for match in self.rx_if.finditer(v):
            ifname = "%s%s" % (match.group("ifname"), match.group("ifnum"))
            iftype = {
                "meth": "management",
                "null": "null",
                "vlanif": "SVI"
            }[match.group("ifname").lower()]
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": match.group("admin_status") != "DOWN",
                "oper_status": match.group("oper_status") != "DOWN",
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": match.group("admin_status") != "DOWN",
                    "oper_status": match.group("oper_status") != "DOWN",
                    "mtu": int(match.group("mtu"))
                }]
            }
            if match.group("descr"):
                iface["description"] = match.group("descr")
                iface["subinterfaces"][0]["description"] = match.group("descr")
            if match.group("ip"):
                iface["subinterfaces"][0]["ipv4_addresses"] = [match.group("ip")]
                iface["subinterfaces"][0]["enabled_afi"] = ['IPv4']
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                iface["subinterfaces"][0]["mac"] = match.group("mac")
            if match.group("ifname") == "vlanif":
                iface["subinterfaces"][0]["vlan_ids"] = int(match.group("ifnum"))
            interfaces += [iface]
        return [{"interfaces": interfaces}]
